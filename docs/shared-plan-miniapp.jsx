import { useState, useCallback } from "react";

const MOCK = {
  user: { id: 1, name: "Иван", isAdmin: true },
  spaces: [
    { id: 1, name: "Семья", membersCount: 4, eventsCount: 5, inviteCode: "xK9mZp2w", role: "admin" },
    { id: 2, name: "Работа — дизайн", membersCount: 7, eventsCount: 3, inviteCode: "aB3nYq8r", role: "member" },
    { id: 3, name: "Футбол по четвергам", membersCount: 12, eventsCount: 1, inviteCode: "pL5vWd4s", role: "member" },
  ],
  members: {
    1: [
      { id: 1, name: "Иван", username: "ivan_dev", role: "admin" },
      { id: 2, name: "Мария", username: "masha_k", role: "member" },
      { id: 3, name: "Алексей", username: "alex99", role: "member" },
      { id: 4, name: "Анна", username: "anna_sun", role: "member" },
    ],
    2: [
      { id: 5, name: "Дмитрий", username: "dima_lead", role: "admin" },
      { id: 1, name: "Иван", username: "ivan_dev", role: "member" },
      { id: 6, name: "Ольга", username: "olga_ux", role: "member" },
    ],
  },
  events: {
    1: [
      { id: 1, title: "Ужин с родителями", date: "2026-03-29", time: "19:00", author: "Иван", spaceId: 1 },
      { id: 2, title: "День рождения Ани", date: "2026-04-05", time: null, author: "Мария", spaceId: 1 },
      { id: 3, title: "Стоматолог", date: "2026-04-10", time: "14:30", author: "Иван", spaceId: 1 },
      { id: 4, title: "Родительское собрание", date: "2026-04-15", time: "18:00", author: "Мария", spaceId: 1 },
      { id: 5, title: "Поездка на дачу", date: "2026-04-20", time: null, author: "Алексей", spaceId: 1 },
    ],
    2: [
      { id: 6, title: "Ревью спринта", date: "2026-03-31", time: "11:00", author: "Дмитрий", spaceId: 2 },
      { id: 7, title: "Дизайн-критика", date: "2026-04-02", time: "15:00", author: "Ольга", spaceId: 2 },
      { id: 8, title: "Ретро Q1", date: "2026-04-04", time: "16:00", author: "Дмитрий", spaceId: 2 },
    ],
    3: [
      { id: 9, title: "Матч с «Динамо»", date: "2026-04-03", time: "20:00", author: "Саша", spaceId: 3 },
    ],
  },
  reminders: { "1d": true, "2h": true, "1h": false, "30m": false, "15m": true, "0m": false },
};

const REMINDER_LABELS = {
  "1d": "За 1 день",
  "2h": "За 2 часа",
  "1h": "За 1 час",
  "30m": "За 30 минут",
  "15m": "За 15 минут",
  "0m": "В момент события",
};

const formatRelativeDate = (dateStr) => {
  const d = new Date(dateStr + "T00:00:00");
  const today = new Date("2026-03-28T00:00:00");
  const diff = Math.round((d - today) / 86400000);
  if (diff === 0) return "Сегодня";
  if (diff === 1) return "Завтра";
  if (diff === 2) return "Послезавтра";
  const months = ["янв", "фев", "мар", "апр", "мая", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"];
  return `${d.getDate()} ${months[d.getMonth()]}`;
};

const initials = (name) => name.split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase();

const COLORS = ["#7F77DD", "#1D9E75", "#D85A30", "#D4537E", "#378ADD", "#639922", "#BA7517"];
const colorFor = (id) => COLORS[id % COLORS.length];

const ChevronRight = () => (
  <svg width="7" height="12" viewBox="0 0 7 12" fill="none" style={{ flexShrink: 0 }}>
    <path d="M1 1L5.5 6L1 11" stroke="#999" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const IconCalendar = () => (
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
    <rect x="1.5" y="3" width="15" height="13" rx="2" stroke="currentColor" strokeWidth="1.2"/>
    <path d="M1.5 7.5H16.5" stroke="currentColor" strokeWidth="1.2"/>
    <path d="M5.5 1.5V4.5M12.5 1.5V4.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
  </svg>
);

const IconClock = () => (
  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
    <circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="1.1"/>
    <path d="M7 4.5V7.5L9 9" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
  </svg>
);

const IconPeople = () => (
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
    <circle cx="7" cy="6" r="2.5" stroke="currentColor" strokeWidth="1.2"/>
    <path d="M2 15c0-2.76 2.24-5 5-5s5 2.24 5 5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
    <circle cx="12.5" cy="6.5" r="2" stroke="currentColor" strokeWidth="1.1"/>
    <path d="M13 10c1.86.5 3.2 2.1 3.5 4" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
  </svg>
);

const IconBell = () => (
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
    <path d="M6.5 14.5c0 1.38 1.12 2 2.5 2s2.5-.62 2.5-2" stroke="currentColor" strokeWidth="1.2"/>
    <path d="M3.5 11.5c0 0 1-1 1-4 0-2.49 2.01-4.5 4.5-4.5s4.5 2.01 4.5 4.5c0 3 1 4 1 4H3.5z" stroke="currentColor" strokeWidth="1.2" strokeLinejoin="round"/>
  </svg>
);

const IconLink = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
    <path d="M6.5 9.5l3-3M5.5 7L4 8.5a2.83 2.83 0 004 4L9.5 11M10.5 9l1.5-1.5a2.83 2.83 0 00-4-4L6.5 5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
  </svg>
);

const IconTrash = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
    <path d="M3 4.5h10M6 4.5V3a1 1 0 011-1h2a1 1 0 011 1v1.5" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
    <path d="M4 4.5l.7 8.5a1 1 0 001 .9h4.6a1 1 0 001-.9l.7-8.5" stroke="currentColor" strokeWidth="1.1"/>
  </svg>
);

const IconEdit = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
    <path d="M9.5 3.5l3 3M3 10.5l6.5-6.5 3 3L6 13.5H3v-3z" stroke="currentColor" strokeWidth="1.1" strokeLinejoin="round"/>
  </svg>
);

const IconBack = () => (
  <svg width="10" height="16" viewBox="0 0 10 16" fill="none">
    <path d="M8.5 1.5L2 8l6.5 6.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const IconPerson = () => (
  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
    <circle cx="7" cy="4.5" r="2.5" stroke="currentColor" strokeWidth="1.1"/>
    <path d="M2.5 13c0-2.49 2.01-4.5 4.5-4.5s4.5 2.01 4.5 4.5" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
  </svg>
);

const IconCheck = () => (
  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
    <path d="M3 7.5l2.5 2.5L11 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const IconPlus = () => (
  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
    <path d="M10 4V16M4 10H16" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/>
  </svg>
);


export default function SharedPlanMiniApp() {
  const [screen, setScreen] = useState("spaces");
  const [history, setHistory] = useState([]);
  const [selectedSpace, setSelectedSpace] = useState(null);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [spaces, setSpaces] = useState(MOCK.spaces);
  const [events, setEvents] = useState(MOCK.events);
  const [reminders, setReminders] = useState(MOCK.reminders);
  const [editingSpaceName, setEditingSpaceName] = useState("");
  const [editingEvent, setEditingEvent] = useState(null);
  const [copiedLink, setCopiedLink] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(null);
  const [toast, setToast] = useState(null);
  const [newSpaceName, setNewSpaceName] = useState("");

  const showToast = (msg) => { setToast(msg); setTimeout(() => setToast(null), 2000); };

  const navigate = useCallback((to, params = {}) => {
    setHistory(h => [...h, { screen, selectedSpace, selectedEvent }]);
    if (params.space !== undefined) setSelectedSpace(params.space);
    if (params.event !== undefined) setSelectedEvent(params.event);
    setScreen(to);
    setConfirmDelete(null);
  }, [screen, selectedSpace, selectedEvent]);

  const goBack = useCallback(() => {
    if (history.length === 0) return;
    const prev = history[history.length - 1];
    setHistory(h => h.slice(0, -1));
    setScreen(prev.screen);
    setSelectedSpace(prev.selectedSpace);
    setSelectedEvent(prev.selectedEvent);
    setConfirmDelete(null);
  }, [history]);

  const headerTitle = {
    spaces: "Пространства",
    spaceCreate: "Новое пространство",
    spaceDetail: selectedSpace?.name || "",
    spaceEdit: "Редактировать",
    members: "Участники",
    eventDetail: "Событие",
    reminders: "Напоминания",
  };

  const space = selectedSpace;
  const isAdmin = space?.role === "admin";

  const Header = ({ title, right }) => (
    <div style={{
      height: 56, display: "flex", alignItems: "center", padding: "0 4px",
      borderBottom: "0.5px solid #e5e5e5", background: "#fff", position: "sticky", top: 0, zIndex: 10,
      flexShrink: 0,
    }}>
      {screen !== "spaces" && (
        <button onClick={goBack} style={{
          width: 44, height: 44, display: "flex", alignItems: "center", justifyContent: "center",
          background: "none", border: "none", cursor: "pointer", color: "#378ADD",
        }}><IconBack /></button>
      )}
      <span style={{
        flex: 1, fontSize: 17, fontWeight: 600,
        paddingLeft: screen === "spaces" ? 16 : 0,
        overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
      }}>{title}</span>
      {right}
    </div>
  );

  const ListItem = ({ left, title, subtitle, right, onClick, danger, compact }) => (
    <button onClick={onClick} style={{
      display: "flex", alignItems: "center", gap: 12,
      padding: compact ? "10px 16px" : "14px 16px", width: "100%",
      background: "none", border: "none", cursor: onClick ? "pointer" : "default",
      textAlign: "left", fontSize: 15,
    }}>
      {left}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{
          fontWeight: 500, color: danger ? "#E24B4A" : "#1a1a1a",
          overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
        }}>{title}</div>
        {subtitle && <div style={{ fontSize: 13, color: "#8e8e93", marginTop: 2 }}>{subtitle}</div>}
      </div>
      {right}
    </button>
  );

  const Avatar = ({ name, size = 42, id = 0 }) => (
    <div style={{
      width: size, height: size, borderRadius: "50%", background: colorFor(id),
      display: "flex", alignItems: "center", justifyContent: "center",
      color: "#fff", fontSize: size * 0.35, fontWeight: 600, flexShrink: 0,
      letterSpacing: 0.5,
    }}>{initials(name)}</div>
  );

  const Section = ({ title, children }) => (
    <div style={{ marginBottom: 8 }}>
      {title && <div style={{
        fontSize: 12, fontWeight: 600, color: "#8e8e93", textTransform: "uppercase",
        letterSpacing: 0.8, padding: "20px 16px 8px",
      }}>{title}</div>}
      <div style={{ background: "#fff", borderTop: "0.5px solid #e5e5e5", borderBottom: "0.5px solid #e5e5e5" }}>
        {children}
      </div>
    </div>
  );

  const Divider = () => <div style={{ height: 0.5, background: "#e5e5e5", marginLeft: 70 }} />;

  const Toggle = ({ on, onToggle }) => (
    <button onClick={onToggle} style={{
      width: 48, height: 28, borderRadius: 14, padding: 2,
      background: on ? "#1D9E75" : "#e5e5e5", border: "none", cursor: "pointer",
      transition: "background 0.2s", flexShrink: 0, position: "relative",
    }}>
      <div style={{
        width: 24, height: 24, borderRadius: 12, background: "#fff",
        transition: "transform 0.2s", transform: on ? "translateX(20px)" : "translateX(0)",
        boxShadow: "0 1px 3px rgba(0,0,0,0.15)",
      }} />
    </button>
  );

  const ActionButton = ({ icon, label, color = "#378ADD", onClick }) => (
    <button onClick={onClick} style={{
      display: "flex", flexDirection: "column", alignItems: "center", gap: 6,
      background: "none", border: "none", cursor: "pointer", padding: "8px 4px", minWidth: 64,
    }}>
      <div style={{
        width: 44, height: 44, borderRadius: 12, background: color + "14",
        display: "flex", alignItems: "center", justifyContent: "center", color,
      }}>{icon}</div>
      <span style={{ fontSize: 11, color, fontWeight: 500 }}>{label}</span>
    </button>
  );

  const renderSpaces = () => (
    <div style={{ background: "#f2f2f7", minHeight: "100%" }}>
      <Section>
        {spaces.map((s, i) => (
          <div key={s.id}>
            {i > 0 && <Divider />}
            <ListItem
              left={<Avatar name={s.name} id={s.id} />}
              title={s.name}
              subtitle={`${s.membersCount} участн. · ${s.eventsCount} событий`}
              right={<ChevronRight />}
              onClick={() => navigate("spaceDetail", { space: s })}
            />
          </div>
        ))}
      </Section>

      <Section title="Настройки">
        <ListItem
          left={<div style={{ width: 42, height: 42, borderRadius: 12, background: "#BA751714", display: "flex", alignItems: "center", justifyContent: "center", color: "#BA7517" }}><IconBell /></div>}
          title="Напоминания"
          subtitle="Настроить интервалы"
          right={<ChevronRight />}
          onClick={() => navigate("reminders")}
        />
      </Section>
    </div>
  );

  const renderSpaceDetail = () => {
    const spaceEvents = events[space.id] || [];
    const members = MOCK.members[space.id] || [];
    return (
      <div style={{ background: "#f2f2f7", minHeight: "100%" }}>
        <div style={{ display: "flex", justifyContent: "center", gap: 12, padding: "16px 16px 8px", background: "#fff", borderBottom: "0.5px solid #e5e5e5" }}>
          {isAdmin && <ActionButton icon={<IconEdit />} label="Изменить" onClick={() => { setEditingSpaceName(space.name); navigate("spaceEdit"); }} />}
          <ActionButton icon={<IconPeople />} label="Участники" onClick={() => navigate("members")} />
          <ActionButton icon={<IconLink />} label="Ссылка" color="#7F77DD"
            onClick={() => { setCopiedLink(true); showToast("Ссылка скопирована"); setTimeout(() => setCopiedLink(false), 2000); }}
          />
          {isAdmin && <ActionButton icon={<IconTrash />} label="Удалить" color="#E24B4A"
            onClick={() => setConfirmDelete("space")}
          />}
        </div>

        {confirmDelete === "space" && (
          <div style={{ margin: 16, padding: 16, background: "#FCEBEB", borderRadius: 12 }}>
            <div style={{ fontSize: 14, fontWeight: 500, color: "#A32D2D", marginBottom: 12 }}>
              Удалить «{space.name}»? Все события и напоминания будут потеряны.
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <button onClick={() => {
                setSpaces(s => s.filter(x => x.id !== space.id));
                setHistory([]);
                setScreen("spaces");
                showToast("Пространство удалено");
              }} style={{
                flex: 1, padding: "10px 0", borderRadius: 10, border: "none",
                background: "#E24B4A", color: "#fff", fontWeight: 600, fontSize: 14, cursor: "pointer",
              }}>Удалить</button>
              <button onClick={() => setConfirmDelete(null)} style={{
                flex: 1, padding: "10px 0", borderRadius: 10, border: "0.5px solid #ddd",
                background: "#fff", color: "#1a1a1a", fontWeight: 500, fontSize: 14, cursor: "pointer",
              }}>Отмена</button>
            </div>
          </div>
        )}

        <Section title={`События · ${spaceEvents.length}`}>
          {spaceEvents.length === 0 ? (
            <div style={{ padding: "32px 16px", textAlign: "center", color: "#8e8e93", fontSize: 14 }}>
              Нет предстоящих событий. Создайте событие через бота.
            </div>
          ) : spaceEvents.map((ev, i) => (
            <div key={ev.id}>
              {i > 0 && <Divider />}
              <ListItem
                left={
                  <div style={{
                    width: 42, height: 48, borderRadius: 10, background: "#f2f2f7",
                    display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
                    border: "0.5px solid #e5e5e5",
                  }}>
                    <span style={{ fontSize: 16, fontWeight: 600, lineHeight: 1.1 }}>
                      {new Date(ev.date + "T00:00:00").getDate()}
                    </span>
                    <span style={{ fontSize: 10, color: "#8e8e93", textTransform: "uppercase", fontWeight: 500 }}>
                      {["янв","фев","мар","апр","мая","июн","июл","авг","сен","окт","ноя","дек"][new Date(ev.date + "T00:00:00").getMonth()]}
                    </span>
                  </div>
                }
                title={ev.title}
                subtitle={`${formatRelativeDate(ev.date)}${ev.time ? ` · ${ev.time}` : ""} · ${ev.author}`}
                right={<ChevronRight />}
                onClick={() => {
                  setEditingEvent({ ...ev });
                  navigate("eventDetail", { event: ev });
                }}
              />
            </div>
          ))}
        </Section>
      </div>
    );
  };

  const renderSpaceEdit = () => (
    <div style={{ background: "#f2f2f7", minHeight: "100%" }}>
      <Section title="Название пространства">
        <div style={{ padding: "8px 16px 12px" }}>
          <input
            value={editingSpaceName}
            onChange={e => setEditingSpaceName(e.target.value)}
            style={{
              width: "100%", padding: "12px 14px", fontSize: 16, borderRadius: 10,
              border: "0.5px solid #d1d1d6", outline: "none", background: "#fff",
              boxSizing: "border-box",
            }}
            placeholder="Название"
            autoFocus
          />
        </div>
      </Section>
      <div style={{ padding: "12px 16px" }}>
        <button onClick={() => {
          setSpaces(s => s.map(x => x.id === space.id ? { ...x, name: editingSpaceName } : x));
          setSelectedSpace({ ...space, name: editingSpaceName });
          goBack();
          showToast("Сохранено");
        }} style={{
          width: "100%", padding: "14px 0", borderRadius: 12, border: "none",
          background: "#378ADD", color: "#fff", fontSize: 16, fontWeight: 600,
          cursor: "pointer", opacity: editingSpaceName.trim() ? 1 : 0.4,
        }} disabled={!editingSpaceName.trim()}>
          Сохранить
        </button>
      </div>
    </div>
  );

  const renderMembers = () => {
    const members = MOCK.members[space?.id] || [];
    return (
      <div style={{ background: "#f2f2f7", minHeight: "100%" }}>
        <Section title={`${members.length} участников`}>
          {members.map((m, i) => (
            <div key={m.id}>
              {i > 0 && <Divider />}
              <ListItem
                left={<Avatar name={m.name} size={38} id={m.id} />}
                title={m.name}
                subtitle={`@${m.username}${m.role === "admin" ? " · администратор" : ""}`}
                right={isAdmin && m.role !== "admin" ? (
                  <button onClick={(e) => { e.stopPropagation(); setConfirmDelete(m.id); }} style={{
                    padding: "5px 12px", borderRadius: 8, border: "0.5px solid #E24B4A33",
                    background: "#FCEBEB", color: "#E24B4A", fontSize: 12, fontWeight: 600,
                    cursor: "pointer",
                  }}>Удалить</button>
                ) : m.role === "admin" ? (
                  <span style={{
                    fontSize: 11, color: "#7F77DD", background: "#EEEDFE",
                    padding: "3px 10px", borderRadius: 6, fontWeight: 600,
                  }}>admin</span>
                ) : null}
              />
              {confirmDelete === m.id && (
                <div style={{ padding: "8px 16px 12px 70px" }}>
                  <div style={{ padding: 12, background: "#FCEBEB", borderRadius: 10, fontSize: 13 }}>
                    <span style={{ color: "#A32D2D" }}>Удалить {m.name} из пространства?</span>
                    <div style={{ display: "flex", gap: 8, marginTop: 10 }}>
                      <button onClick={() => { setConfirmDelete(null); showToast(`${m.name} удалён`); }} style={{
                        padding: "7px 16px", borderRadius: 8, border: "none",
                        background: "#E24B4A", color: "#fff", fontSize: 12, fontWeight: 600, cursor: "pointer",
                      }}>Да, удалить</button>
                      <button onClick={() => setConfirmDelete(null)} style={{
                        padding: "7px 16px", borderRadius: 8, border: "0.5px solid #ddd",
                        background: "#fff", fontSize: 12, cursor: "pointer",
                      }}>Отмена</button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </Section>

        <div style={{ padding: "16px", fontSize: 13, color: "#8e8e93", textAlign: "center", lineHeight: 1.5 }}>
          Новые участники присоединяются по invite-ссылке пространства
        </div>
      </div>
    );
  };

  const renderEventDetail = () => {
    const ev = editingEvent;
    if (!ev) return null;
    return (
      <div style={{ background: "#f2f2f7", minHeight: "100%" }}>
        <Section title="Детали события">
          <div style={{ padding: "12px 16px" }}>
            <label style={{ fontSize: 12, color: "#8e8e93", fontWeight: 500, display: "block", marginBottom: 6 }}>Название</label>
            <input
              value={ev.title}
              onChange={e => setEditingEvent({ ...ev, title: e.target.value })}
              style={{
                width: "100%", padding: "11px 14px", fontSize: 16, borderRadius: 10,
                border: "0.5px solid #d1d1d6", outline: "none", background: "#fff",
                boxSizing: "border-box",
              }}
            />
          </div>
          <div style={{ height: 0.5, background: "#e5e5e5", marginLeft: 16 }} />
          <div style={{ padding: "12px 16px", display: "flex", gap: 12 }}>
            <div style={{ flex: 1 }}>
              <label style={{ fontSize: 12, color: "#8e8e93", fontWeight: 500, display: "block", marginBottom: 6 }}>Дата</label>
              <input
                type="date"
                value={ev.date}
                onChange={e => setEditingEvent({ ...ev, date: e.target.value })}
                style={{
                  width: "100%", padding: "11px 14px", fontSize: 15, borderRadius: 10,
                  border: "0.5px solid #d1d1d6", outline: "none", background: "#fff",
                  boxSizing: "border-box",
                }}
              />
            </div>
            <div style={{ flex: 1 }}>
              <label style={{ fontSize: 12, color: "#8e8e93", fontWeight: 500, display: "block", marginBottom: 6 }}>Время</label>
              <input
                type="time"
                value={ev.time || ""}
                onChange={e => setEditingEvent({ ...ev, time: e.target.value || null })}
                style={{
                  width: "100%", padding: "11px 14px", fontSize: 15, borderRadius: 10,
                  border: "0.5px solid #d1d1d6", outline: "none", background: "#fff",
                  boxSizing: "border-box",
                }}
                placeholder="—"
              />
            </div>
          </div>
        </Section>

        <Section>
          <div style={{ padding: "12px 16px", display: "flex", alignItems: "center", gap: 10, color: "#8e8e93" }}>
            <IconPerson />
            <span style={{ fontSize: 14 }}>Создал: {ev.author}</span>
          </div>
        </Section>

        <div style={{ padding: "12px 16px", display: "flex", gap: 10 }}>
          <button onClick={() => {
            setEvents(evs => ({
              ...evs,
              [ev.spaceId]: evs[ev.spaceId].map(x => x.id === ev.id ? editingEvent : x),
            }));
            goBack();
            showToast("Событие обновлено");
          }} style={{
            flex: 1, padding: "14px 0", borderRadius: 12, border: "none",
            background: "#378ADD", color: "#fff", fontSize: 16, fontWeight: 600, cursor: "pointer",
          }}>Сохранить</button>
        </div>

        <div style={{ padding: "0 16px" }}>
          <button onClick={() => {
            setConfirmDelete("event");
          }} style={{
            width: "100%", padding: "14px 0", borderRadius: 12,
            border: "0.5px solid #E24B4A33", background: "#FCEBEB",
            color: "#E24B4A", fontSize: 15, fontWeight: 600, cursor: "pointer",
          }}>Удалить событие</button>
        </div>

        {confirmDelete === "event" && (
          <div style={{ margin: 16, padding: 16, background: "#FCEBEB", borderRadius: 12 }}>
            <div style={{ fontSize: 14, fontWeight: 500, color: "#A32D2D", marginBottom: 12 }}>
              Удалить «{ev.title}»? Напоминания тоже будут удалены.
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <button onClick={() => {
                setEvents(evs => ({
                  ...evs,
                  [ev.spaceId]: evs[ev.spaceId].filter(x => x.id !== ev.id),
                }));
                goBack();
                showToast("Событие удалено");
              }} style={{
                flex: 1, padding: "10px 0", borderRadius: 10, border: "none",
                background: "#E24B4A", color: "#fff", fontWeight: 600, fontSize: 14, cursor: "pointer",
              }}>Удалить</button>
              <button onClick={() => setConfirmDelete(null)} style={{
                flex: 1, padding: "10px 0", borderRadius: 10, border: "0.5px solid #ddd",
                background: "#fff", fontSize: 14, cursor: "pointer",
              }}>Отмена</button>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderReminders = () => (
    <div style={{ background: "#f2f2f7", minHeight: "100%" }}>
      <Section title="Интервалы напоминаний">
        {Object.entries(REMINDER_LABELS).map(([key, label], i) => (
          <div key={key}>
            {i > 0 && <div style={{ height: 0.5, background: "#e5e5e5", marginLeft: 16 }} />}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 16px" }}>
              <span style={{ fontSize: 15 }}>{label}</span>
              <Toggle on={reminders[key]} onToggle={() => setReminders(r => ({ ...r, [key]: !r[key] }))} />
            </div>
          </div>
        ))}
      </Section>

      <div style={{ padding: "8px 16px", fontSize: 13, color: "#8e8e93", lineHeight: 1.5 }}>
        Настройки применяются ко всем новым событиям во всех пространствах.
        Уже созданные напоминания не изменятся.
      </div>
    </div>
  );

  const renderSpaceCreate = () => (
    <div style={{ background: "#f2f2f7", minHeight: "100%" }}>
      <Section title="Название пространства">
        <div style={{ padding: "8px 16px 12px" }}>
          <input
            value={newSpaceName}
            onChange={e => setNewSpaceName(e.target.value)}
            style={{
              width: "100%", padding: "12px 14px", fontSize: 16, borderRadius: 10,
              border: "0.5px solid #d1d1d6", outline: "none", background: "#fff",
              boxSizing: "border-box",
            }}
            placeholder="Например, «Семья» или «Работа»"
            autoFocus
          />
        </div>
      </Section>
      <div style={{ padding: "12px 16px" }}>
        <button onClick={() => {
          const id = Date.now();
          const code = Math.random().toString(36).slice(2, 10);
          const newSpace = {
            id, name: newSpaceName.trim(), membersCount: 1, eventsCount: 0,
            inviteCode: code, role: "admin",
          };
          setSpaces(s => [...s, newSpace]);
          setEvents(evs => ({ ...evs, [id]: [] }));
          setHistory([]);
          setScreen("spaces");
          showToast("Пространство создано");
        }} style={{
          width: "100%", padding: "14px 0", borderRadius: 12, border: "none",
          background: "#378ADD", color: "#fff", fontSize: 16, fontWeight: 600,
          cursor: "pointer", opacity: newSpaceName.trim() ? 1 : 0.4,
        }} disabled={!newSpaceName.trim()}>
          Создать
        </button>
      </div>
      <div style={{ padding: "8px 16px", fontSize: 13, color: "#8e8e93", lineHeight: 1.5 }}>
        Вы станете администратором. Пригласите участников по ссылке после создания.
      </div>
    </div>
  );

  const screens = {
    spaces: renderSpaces,
    spaceCreate: renderSpaceCreate,
    spaceDetail: renderSpaceDetail,
    spaceEdit: renderSpaceEdit,
    members: renderMembers,
    eventDetail: renderEventDetail,
    reminders: renderReminders,
  };

  return (
    <div style={{ display: "flex", justifyContent: "center", padding: "0" }}>
      <div style={{
        width: 375, minHeight: 700, background: "#f2f2f7",
        borderRadius: 20, overflow: "hidden",
        border: "0.5px solid #d1d1d6",
        display: "flex", flexDirection: "column",
        boxShadow: "0 4px 24px rgba(0,0,0,0.08)",
        position: "relative",
      }}>
        <Header
          title={headerTitle[screen]}
          right={screen === "spaces" ? (
            <button onClick={() => { setNewSpaceName(""); navigate("spaceCreate"); }} style={{
              width: 44, height: 44, display: "flex", alignItems: "center", justifyContent: "center",
              background: "none", border: "none", cursor: "pointer", color: "#378ADD", marginRight: 4,
            }}><IconPlus /></button>
          ) : null}
        />

        <div style={{ flex: 1, overflowY: "auto" }}>
          {screens[screen]?.()}
        </div>

        {toast && (
          <div style={{
            position: "absolute", bottom: 32, left: "50%", transform: "translateX(-50%)",
            background: "#1a1a1a", color: "#fff", padding: "10px 20px", borderRadius: 20,
            fontSize: 14, fontWeight: 500, whiteSpace: "nowrap",
            animation: "fadeInUp 0.2s ease",
          }}>
            {toast}
          </div>
        )}
      </div>

      <style>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateX(-50%) translateY(8px); }
          to { opacity: 1; transform: translateX(-50%) translateY(0); }
        }
        input[type="date"], input[type="time"] {
          -webkit-appearance: none;
          font-family: inherit;
        }
      `}</style>
    </div>
  );
}
