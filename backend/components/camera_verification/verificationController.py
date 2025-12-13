from flask import Blueprint, request, jsonify

from backend.components.camera_verification.qrcode.qrcodeService import (
    getWorkerFromQRCode,
)
from backend.components.camera_verification.faceid.faceidService import (
    verifyWorkerFace
)
from backend.components.utils.imageUtils import (
    parseImage
)


bp = Blueprint('bp_verification', __name__)


@bp.route('/api/skan', methods=['POST'])
def post_camera_scan():
    if 'file' not in request.files:
        return jsonify({'error': 'Brak pliku w żądaniu (oczekiwano klucza "file").'}), 400

    # Load and parse image
    img = parseImage(request.files['file'])

    try:
        worker = getWorkerFromQRCode(img)
        worker_valid = verifyWorkerFace(worker, img)
        if worker_valid:
            return jsonify({'code': 0, 'text': 'Verification successful.'})
        else:
            raise WorkerCodeMismatchError("Znaleziony kod nie zgadza się z pracownikiem")

    except Exception as e:
        return jsonify({'error': str(e)}), 400  # TODO: Fix, add proper error handling


class WorkerCodeMismatchError(Exception):
    """
    Raised when detected face does not match with database
    """
    pass
