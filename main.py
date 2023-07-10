import requests

from firebase_functions.firestore_fn import (
    on_document_created,
    on_document_updated,
    Event,
    Change,
    DocumentSnapshot,
)


@on_document_created(document="vouchers/{voucherId}", region="us-west1")
def verify_ruc_created(event: Event[DocumentSnapshot]) -> None:
    # Obtener el valor del comprobante creado
    created_voucher = event.data.to_dict()

    # Obtener el RUC del comprobante
    ruc = created_voucher["ruc"]

    # Verificar que el RUC sea correcto (obtener razón social)
    url_verify_ruc = "https://api.migo.pe/api/v1/ruc"
    body_verify_ruc = {"token": "pQRr33428SZcHPQh4pzCHvp78p7QN6XtzcG0SZhI9ySqSIPMf0S8ys8HGsEN", "ruc": ruc}

    response_verify_ruc = requests.post(url_verify_ruc, json=body_verify_ruc)

    if response_verify_ruc.status_code != 200:
        event.data.reference.update({
            "socialReason": "RUC " + ruc + " no encontrado",
            "statusRuc": "Error",
        })
    else:
        event.data.reference.update({
            "socialReason": response_verify_ruc.json()["nombre_o_razon_social"],
            "statusRuc": "Correcto",
        })


@on_document_updated(document="vouchers/{voucherId}", region="us-west1")
def verify_ruc_updated(event: Event[Change[DocumentSnapshot]]) -> None:
    # Obtener el valor del comprobante actualizado
    after_updated_voucher = event.data.after.to_dict()

    # Obtener el RUC del comprobante
    ruc = after_updated_voucher["ruc"]

    # Verificar que el RUC sea correcto (obtener razón social)
    url_verify_ruc = "https://api.migo.pe/api/v1/ruc"
    body_verify_ruc = {"token": "pQRr33428SZcHPQh4pzCHvp78p7QN6XtzcG0SZhI9ySqSIPMf0S8ys8HGsEN", "ruc": ruc}

    response_verify_ruc = requests.post(url_verify_ruc, json=body_verify_ruc)

    if response_verify_ruc.status_code != 200:
        event.data.after.reference.update({
            "socialReason": "RUC " + ruc + " no encontrado",
            "statusRuc": "Error",
        })
    else:
        event.data.after.reference.update({
            "socialReason": response_verify_ruc.json()["nombre_o_razon_social"],
            "statusRuc": "Correcto",
        })


@on_document_created(document="vouchers/{voucherId}", region="us-west1")
def verify_voucher_created(event: Event[DocumentSnapshot]) -> None:
    # Obtener el valor del comprobante creado
    created_voucher = event.data.to_dict()

    # Obtener RUC, tipo, serie, número, fecha y monto del comprobante
    ruc = created_voucher["ruc"]
    type = "01" if created_voucher["voucherType"] == "Factura" else "03"
    serial = created_voucher["serial"]
    number = created_voucher["number"]
    date = created_voucher["date"]
    amount = created_voucher["amount"]

    # Verificar que el comprobante sea correcto (verificar que esté en la SUNAT)
    url_verify_ruc = "https://api.migo.pe/api/v1/cpe"
    body_verify_ruc = {
        "token": "pQRr33428SZcHPQh4pzCHvp78p7QN6XtzcG0SZhI9ySqSIPMf0S8ys8HGsEN",
        "ruc_emisor": ruc,
        "tipo_comprobante": type,
        "serie": serial,
        "numero": number,
        "fecha_emision": date.strftime("%d/%m/%Y"),
        "monto": str(round(amount, 2)),
    }

    response_verify_voucher = requests.post(url_verify_ruc, json=body_verify_ruc)

    try:
        status = response_verify_voucher.json()["estado_comprobante"]

        if status != "1":
            event.data.reference.update({
                "statusVoucher": "Error",
            })
        else:
            event.data.reference.update({
                "statusVoucher": "Correcto",
            })
    except:
        event.data.reference.update({
            "statusVoucher": "Error",
        })


@on_document_updated(document="vouchers/{voucherId}", region="us-west1")
def verify_voucher_updated(event: Event[Change[DocumentSnapshot]]) -> None:
    # Obtener el valor del comprobante actualizado
    after_updated_voucher = event.data.after.to_dict()

    # Obtener RUC, tipo, serie, número, fecha y monto del comprobante
    ruc = after_updated_voucher["ruc"]
    type = "01" if after_updated_voucher["voucherType"] == "Factura" else "03"
    serial = after_updated_voucher["serial"]
    number = after_updated_voucher["number"]
    date = after_updated_voucher["date"]
    amount = after_updated_voucher["amount"]

    # Verificar que el comprobante sea correcto (verificar que esté en la SUNAT)
    url_verify_ruc = "https://api.migo.pe/api/v1/cpe"
    body_verify_ruc = {
        "token": "pQRr33428SZcHPQh4pzCHvp78p7QN6XtzcG0SZhI9ySqSIPMf0S8ys8HGsEN",
        "ruc_emisor": ruc,
        "tipo_comprobante": type,
        "serie": serial,
        "numero": number,
        "fecha_emision": date.strftime("%d/%m/%Y"),
        "monto": str(round(amount, 2)),
    }

    response_verify_voucher = requests.post(url_verify_ruc, json=body_verify_ruc)

    try:
        status = response_verify_voucher.json()["estado_comprobante"]

        if status != "1":
            event.data.after.reference.update({
                "statusVoucher": "Error",
            })
        else:
            event.data.after.reference.update({
                "statusVoucher": "Correcto",
            })
    except:
        event.data.after.reference.update({
            "statusVoucher": "Error",
        })

# PS C:\Users\piero\FirebaseFunctions> firebase deploy
# PS C:\Users\piero\FirebaseFunctions\functions> .\venv\Scripts\pip.exe freeze > requirements.txt
