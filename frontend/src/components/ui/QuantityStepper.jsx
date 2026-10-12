import { MAX_QUANTITY } from "../../stores/cart";

// Kontrol jumlah: tombol 44px (nyaman disentuh), efek timbul tipis (neumorphic ringan).
export default function QuantityStepper({ value, onChange, label, max = MAX_QUANTITY }) {
  return (
    <div className="stepper" role="group" aria-label={`Jumlah ${label}`}>
      <button
        type="button"
        className="stepper__btn"
        aria-label={`Kurangi ${label}`}
        onClick={() => onChange(value - 1)}
      >
        −
      </button>
      <span className="stepper__value" aria-live="polite">
        {value}
      </span>
      <button
        type="button"
        className="stepper__btn"
        aria-label={`Tambah ${label}`}
        disabled={value >= max}
        onClick={() => onChange(value + 1)}
      >
        +
      </button>
    </div>
  );
}
