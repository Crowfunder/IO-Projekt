import base64
import io
import os
from flask import Blueprint, request, jsonify, render_template, make_response, send_file, current_app
from xhtml2pdf import pisa
from xhtml2pdf.files import pisaFileObject
from backend.components.reports.reportService import get_report_data
from datetime import datetime

bp = Blueprint('reports', __name__, url_prefix='/api/raport')


@bp.route('', methods=['GET'])
def generate_report():
    '''
        Retrieves entry report data by joining Entry records with Worker data.

        This function handles filtering by date range, specific worker, and entry validity status.
        Results are sorted in descending order by date.

        **Parameters**:
        - `date_from` (datetime): Start date (inclusive). Defaults to None.
        - `date_to` (datetime): End date (inclusive). Defaults to None.
        - `worker_id` (int): Worker ID to filter by. Defaults to None.
        - `show_valid` (bool): Whether to include valid entries (code 0). If selected together with show_invalid (or both are unselected), returns all types.
        - `show_invalid` (bool): Whether to include invalid entries (code != 0). If selected together with show_valid (or both are unselected), returns all types.

        **Returns**:
        - `List[Tuple[Entry, Optional[Worker]]]` - A list of tuples where the first element is the entry object (Entry) and the second is the worker object (Worker) or None if the entry has no assigned worker.
    '''

    try:
        date_from_str = request.args.get('date_from')
        date_to_str = request.args.get('date_to')
        worker_id = request.args.get('pracownik_id', type=int)

        show_invalid = 'wejscia_niepoprawne' in request.args
        show_valid = 'wejscia_poprawne' in request.args

        date_from = None
        date_to = None

        if date_from_str:
            try:
                date_from = datetime.fromisoformat(date_from_str)
            except ValueError:
                return jsonify({'error': 'Nieprawidłowy format date_from. Oczekiwano YYYY-MM-DD'}), 400

        if date_to_str:
            try:
                date_to = datetime.fromisoformat(date_to_str)
                if len(date_to_str) == 10:
                    date_to = date_to.replace(hour=23, minute=59, second=59, microsecond=999999)
            except ValueError:
                return jsonify({'error': 'Nieprawidłowy format date_to'}), 400

        results = get_report_data(
            date_from=date_from,
            date_to=date_to,
            worker_id=worker_id,
            show_valid=show_valid,
            show_invalid=show_invalid
        )

        report_data = []
        for entry, worker in results:
            # Kodowanie obrazu do Base64
            encoded_image = None
            if entry.face_image:
                encoded_image = base64.b64encode(entry.face_image).decode('utf-8')

            report_data.append({
                'id': entry.id,
                'date': entry.date.isoformat(),
                'code': entry.code,
                'message': entry.message,
                'worker_id': entry.worker_id,
                'worker_name': worker.name if worker else 'Nieznany',
                'face_image': encoded_image
            })

        return jsonify({
            'count': len(report_data),
            'filters': {
                'date_from': date_from_str,
                'date_to': date_to_str,
                'worker_id': worker_id,
                'show_valid': show_valid,
                'show_invalid': show_invalid
            },
            'data': report_data
        })

    except Exception as e:
        print(f"Błąd raportu: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/pdf', methods=['GET'])
def generate_pdf_report():
    """
    Generuje raport w formacie PDF na podstawie zadanych filtrów.
    Pobiera dokładnie te same parametry co wersja JSON.
    """
    try:
        date_from_str = request.args.get('date_from')
        date_to_str = request.args.get('date_to')
        worker_id = request.args.get('pracownik_id', type=int)

        show_invalid = 'wejscia_niepoprawne' in request.args
        show_valid = 'wejscia_poprawne' in request.args

        date_from = None
        date_to = None

        if date_from_str:
            try:
                date_from = datetime.fromisoformat(date_from_str)
            except ValueError:
                return jsonify({'error': 'Nieprawidłowy format date_from'}), 400

        if date_to_str:
            try:
                date_to = datetime.fromisoformat(date_to_str)
                # Jeśli podano samą datę (format YYYY-MM-DD, bez godziny), ustawiamy czas na koniec dnia,
                # aby uwzględnić wszystkie wpisy z tego dnia (domyślnie fromisoformat ustawia 00:00:00).
                if len(date_to_str) == 10:
                    date_to = date_to.replace(hour=23, minute=59, second=59, microsecond=999999)
            except ValueError:
                return jsonify({'error': 'Nieprawidłowy format date_to'}), 400

        # --- 2. Pobranie danych ---
        results = get_report_data(
            date_from=date_from,
            date_to=date_to,
            worker_id=worker_id,
            show_valid=show_valid,
            show_invalid=show_invalid
        )

        # --- 3. Przygotowanie danych dla szablonu HTML ---
        report_data = []
        for entry, worker in results:
            # Konwersja obrazka na Base64 (dla HTML)
            img_b64 = None
            if entry.face_image:
                img_b64 = base64.b64encode(entry.face_image).decode('utf-8')

            report_data.append({
                'id': entry.id,
                'date': entry.date.strftime('%Y-%m-%d %H:%M:%S'),
                'code': entry.code,
                'message': entry.message,
                'worker_id': entry.worker_id,
                'worker_name': worker.name if worker else 'Nieznany',
                'face_image_b64': img_b64
            })

        font_path = os.path.join(current_app.config['STATIC_FOLDER'], 'fonts', 'Roboto-Regular.ttf')

        context = {
            'data': report_data,
            'count': len(report_data),
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'filters': {
                'date_from': date_from_str,
                'date_to': date_to_str,
                'worker_id': worker_id,
                'show_valid': show_valid,
                'show_invalid': show_invalid
            },
            'font_path': font_path
        }

        # --- 4. Renderowanie HTML i konwersja na PDF ---
        html_content = render_template('reports/report_pdf.html', **context)

        pdf_output = io.BytesIO()

        # On windows, file paths to the font break
        # known issue, applying a monkeypatch
        # https://github.com/xhtml2pdf/xhtml2pdf/issues/623#issuecomment-1372719452
        pisaFileObject.getNamedFile = lambda self: self.uri 
        pisa_status = pisa.CreatePDF(
            io.BytesIO(html_content.encode('utf-8')),
            dest=pdf_output,
            encoding='utf-8'
        )

        if pisa_status.err:
            return jsonify({'error': 'Błąd podczas generowania PDF'}), 500

        pdf_output.seek(0)

        return send_file(
            pdf_output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"raport_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        )

    except Exception as e:
        print(f"Błąd generowania PDF: {e}")
        return jsonify({'error': str(e)}), 500