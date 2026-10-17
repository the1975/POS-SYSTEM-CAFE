import { ROLE_LABEL } from "../../stores/auth";

export default function StaffHeader({ title, user, onLogout }) {
  return (
    <header className="header">
      <div className="container header__inner staff-bar">
        <span className="brand">{title}</span>
        {user && (
          <span className="staff-bar__user">
            <span className="staff-bar__who">
              <span>{user.name}</span>
              <span className="muted">{ROLE_LABEL[user.role] ?? user.role}</span>
            </span>
            <button type="button" className="link-btn" onClick={onLogout}>
              Keluar
            </button>
          </span>
        )}
      </div>
    </header>
  );
}
