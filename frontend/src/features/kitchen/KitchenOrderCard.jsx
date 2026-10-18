import { LATE_MINUTES, canMarkReady, canRemake, elapsedMinutes, formatElapsed, itemStatusLabel } from "./kitchen";

// Prioritas kartu (wireframes.md #14): nomor order, item, jumlah, status, pewaktu, aksi.
export default function KitchenOrderCard({ order, now, busy, onStart, onReady, onRemake }) {
  const cooking = order.status === "PREPARING";
  const since = cooking ? order.preparing_at ?? order.confirmed_at : order.confirmed_at;
  const minutes = elapsedMinutes(since, now);
  const late = minutes != null && minutes >= LATE_MINUTES;

  return (
    <li className="surface kcard">
      <div className="kcard__head">
        <span className="kcard__no">{order.order_number}</span>
        <span className={`kcard__time${late ? " kcard__time--late" : ""}`}>
          {cooking ? "Dimasak" : "Menunggu"} {formatElapsed(minutes)}
        </span>
      </div>
      <p className="muted">{order.customer_name}</p>

      <ul className="kitems">
        {order.items.map((item) => (
          <li key={item.order_item_id} className="kitem">
            <span className="kitem__name">
              {item.name} ×{item.quantity}
            </span>
            {cooking && (
              <>
                <span className={`pill${item.status === "REMAKE" ? " pill--warn" : ""}`}>
                  {itemStatusLabel(item.status)}
                </span>
                <span className="kitem__actions">
                  {canMarkReady(item) && (
                    <button type="button" className="btn btn--sm" disabled={busy} onClick={() => onReady(item)}>
                      Siap
                    </button>
                  )}
                  {canRemake(item) && (
                    <button
                      type="button"
                      className="btn btn--sm btn--ghost"
                      disabled={busy}
                      onClick={() => onRemake(order, item)}
                    >
                      Remake
                    </button>
                  )}
                </span>
              </>
            )}
          </li>
        ))}
      </ul>

      {!cooking && (
        <button type="button" className="btn btn--block" disabled={busy} onClick={() => onStart(order)}>
          Mulai
        </button>
      )}
    </li>
  );
}
