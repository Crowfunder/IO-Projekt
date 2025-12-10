import cv2
from flask import Blueprint, request, jsonify
from backend.components.camera_verification.qrcode.qrcodeService import (
    decodeQRImage,
    getWorkerByQRCodeSecret,
    MultipleCodesError,
    NoCodeFoundError
)


bp = Blueprint('bp_qrcode', __name__)


@bp.route('/api/skan', methods=['POST'])
def post_camera_scan():
    if 'file' not in request.files:
        return jsonify({'error': 'Brak pliku w żądaniu (oczekiwano klucza "file").'}), 400

    file_st = request.files['file'].stream


    try:
        qr_secret = decodeQRImage(file.stream)
    except Exception as e:
        return jsonify({'error': str(e)}), 400  # TODO: Fix

    return 'ok', 200

