from pydantic import BaseModel


class WebhookOut(BaseModel):
    # "processed" = dijalankan, "duplicate" = event_id sudah pernah, "ignored" = diterima
    # tapi tidak mengubah apa pun. Ketiganya HTTP 200 supaya provider berhenti mengirim ulang.
    result: str
