// Membuat gambar QR (PNG) dan menyimpannya ke HP lewat unduhan browser.
export async function makeQrDataUrl(text, width = 640) {
  const { default: QRCode } = await import("qrcode");
  return QRCode.toDataURL(text, {
    width,
    margin: 2,
    errorCorrectionLevel: "M",
    color: { dark: "#000000", light: "#ffffff" },
  });
}

export async function saveQrImage(text, filename = "qris.png") {
  const url = await makeQrDataUrl(text);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
}
