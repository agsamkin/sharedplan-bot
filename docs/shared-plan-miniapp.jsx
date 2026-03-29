import { useState, useCallback } from "react";

const I18N = {
  ru: {
    spaces: "Пространства", newSpace: "Новое пространство", edit: "Редактировать",
    members: "Участники", newEvent: "Новое событие", event: "Событие",
    reminders: "Напоминания", language: "Язык", settings: "Настройки",
    reminderIntervals: "Интервалы напоминаний",
    reminderHint: "Настройки применяются ко всем новым событиям во всех пространствах. Уже созданные напоминания не изменятся.",
    reminderSubtitle: "Настроить интервалы",
    membersUnit: "участн.", eventsUnit: "событий",
    editAction: "Изменить", membersAction: "Участники", linkAction: "Ссылка", deleteAction: "Удалить",
    linkCopied: "Ссылка скопирована",
    deleteSpaceConfirm: (n) => `Удалить «${n}»? Все события и напоминания будут потеряны.`,
    deleteBtn: "Удалить", cancelBtn: "Отмена", spaceDeleted: "Пространство удалено",
    noEvents: "Нет предстоящих событий", eventsTitle: "События",
    spaceName: "Название пространства", namePlaceholder: "Название",
    save: "Сохранить", saved: "Сохранено",
    membersCount: (n) => `${n} участников`, administrator: "администратор",
    removeMember: "Удалить",
    removeMemberConfirm: (n) => `Удалить ${n} из пространства?`,
    yesRemove: "Да, удалить", memberRemoved: (n) => `${n} удалён`,
    membersInviteHint: "Новые участники присоединяются по invite-ссылке пространства",
    eventDetails: "Детали события", title: "Название", date: "Дата", time: "Время",
    createdBy: "Создал", eventUpdated: "Событие обновлено",
    deleteEvent: "Удалить событие",
    deleteEventConfirm: (t) => `Удалить «${t}»? Напоминания тоже будут удалены.`,
    eventDeleted: "Событие удалено",
    spaceNameLabel: "Название пространства",
    spaceNamePlaceholder: "Например, «Семья» или «Работа»",
    create: "Создать", spaceCreated: "Пространство создано",
    spaceCreateHint: "Вы станете администратором. Пригласите участников по ссылке после создания.",
    eventTitlePlaceholder: "Ужин с друзьями", timeOptional: "(необязательно)",
    createEvent: "Создать событие", eventCreated: "Событие создано",
    eventCreateHint: (n) => `Все участники пространства «${n}» получат уведомление о новом событии.`,
    today: "Сегодня", tomorrow: "Завтра", dayAfter: "Послезавтра",
    months: ["янв","фев","мар","апр","мая","июн","июл","авг","сен","окт","ноя","дек"],
    reminderLabels: { "1d": "За 1 день", "2h": "За 2 часа", "1h": "За 1 час", "30m": "За 30 минут", "15m": "За 15 минут", "0m": "В момент события" },
    langName: "Русский", interfaceLang: "Язык интерфейса",
    repeat: "Повтор",
    repeatOptions: { none: "Не повторять", daily: "Каждый день", weekly: "Каждую неделю", biweekly: "Каждые 2 недели", monthly: "Каждый месяц", yearly: "Каждый год" },
  },
  en: {
    spaces: "Spaces", newSpace: "New space", edit: "Edit",
    members: "Members", newEvent: "New event", event: "Event",
    reminders: "Reminders", language: "Language", settings: "Settings",
    reminderIntervals: "Reminder intervals",
    reminderHint: "Settings apply to all new events across all spaces. Existing reminders won't change.",
    reminderSubtitle: "Set up intervals",
    membersUnit: "members", eventsUnit: "events",
    editAction: "Edit", membersAction: "Members", linkAction: "Link", deleteAction: "Delete",
    linkCopied: "Link copied",
    deleteSpaceConfirm: (n) => `Delete "${n}"? All events and reminders will be lost.`,
    deleteBtn: "Delete", cancelBtn: "Cancel", spaceDeleted: "Space deleted",
    noEvents: "No upcoming events", eventsTitle: "Events",
    spaceName: "Space name", namePlaceholder: "Name",
    save: "Save", saved: "Saved",
    membersCount: (n) => `${n} members`, administrator: "administrator",
    removeMember: "Remove",
    removeMemberConfirm: (n) => `Remove ${n} from the space?`,
    yesRemove: "Yes, remove", memberRemoved: (n) => `${n} removed`,
    membersInviteHint: "New members join via the space invite link",
    eventDetails: "Event details", title: "Title", date: "Date", time: "Time",
    createdBy: "Created by", eventUpdated: "Event updated",
    deleteEvent: "Delete event",
    deleteEventConfirm: (t) => `Delete "${t}"? Reminders will also be removed.`,
    eventDeleted: "Event deleted",
    spaceNameLabel: "Space name",
    spaceNamePlaceholder: 'E.g. "Family" or "Work"',
    create: "Create", spaceCreated: "Space created",
    spaceCreateHint: "You'll become the admin. Invite members via link after creation.",
    eventTitlePlaceholder: "Dinner with friends", timeOptional: "(optional)",
    createEvent: "Create event", eventCreated: "Event created",
    eventCreateHint: (n) => `All members of "${n}" will be notified about the new event.`,
    today: "Today", tomorrow: "Tomorrow", dayAfter: "Day after tomorrow",
    months: ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
    reminderLabels: { "1d": "1 day before", "2h": "2 hours before", "1h": "1 hour before", "30m": "30 min before", "15m": "15 min before", "0m": "At the time of event" },
    langName: "English", interfaceLang: "Interface language",
    repeat: "Repeat",
    repeatOptions: { none: "Never", daily: "Every day", weekly: "Every week", biweekly: "Every 2 weeks", monthly: "Every month", yearly: "Every year" },
  },
};

const MOCK = {
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
      { id: 1, title: "Ужин с родителями", date: "2026-03-29", time: "19:00", author: "Иван", spaceId: 1, repeat: null },
      { id: 2, title: "День рождения Ани", date: "2026-04-05", time: null, author: "Мария", spaceId: 1, repeat: "yearly" },
      { id: 3, title: "Стоматолог", date: "2026-04-10", time: "14:30", author: "Иван", spaceId: 1, repeat: null },
      { id: 4, title: "Родительское собрание", date: "2026-04-15", time: "18:00", author: "Мария", spaceId: 1, repeat: "monthly" },
      { id: 5, title: "Поездка на дачу", date: "2026-04-20", time: null, author: "Алексей", spaceId: 1, repeat: null },
    ],
    2: [
      { id: 6, title: "Ревью спринта", date: "2026-03-31", time: "11:00", author: "Дмитрий", spaceId: 2, repeat: "biweekly" },
      { id: 7, title: "Дизайн-критика", date: "2026-04-02", time: "15:00", author: "Ольга", spaceId: 2, repeat: "weekly" },
      { id: 8, title: "Ретро Q1", date: "2026-04-04", time: "16:00", author: "Дмитрий", spaceId: 2, repeat: null },
    ],
    3: [
      { id: 9, title: "Матч с «Динамо»", date: "2026-04-03", time: "20:00", author: "Саша", spaceId: 3, repeat: "weekly" },
    ],
  },
  reminders: { "1d": true, "2h": true, "1h": false, "30m": false, "15m": true, "0m": false },
};

const initials = (name) => name.split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase();
const COLORS = ["#7F77DD", "#1D9E75", "#D85A30", "#D4537E", "#378ADD", "#639922", "#BA7517"];
const colorFor = (id) => COLORS[id % COLORS.length];

const ChevronRight = () => (<svg width="7" height="12" viewBox="0 0 7 12" fill="none" style={{ flexShrink: 0 }}><path d="M1 1L5.5 6L1 11" stroke="#999" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>);
const IconPeople = () => (<svg width="18" height="18" viewBox="0 0 18 18" fill="none"><circle cx="7" cy="6" r="2.5" stroke="currentColor" strokeWidth="1.2"/><path d="M2 15c0-2.76 2.24-5 5-5s5 2.24 5 5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/><circle cx="12.5" cy="6.5" r="2" stroke="currentColor" strokeWidth="1.1"/><path d="M13 10c1.86.5 3.2 2.1 3.5 4" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/></svg>);
const IconBell = () => (<svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M6.5 14.5c0 1.38 1.12 2 2.5 2s2.5-.62 2.5-2" stroke="currentColor" strokeWidth="1.2"/><path d="M3.5 11.5c0 0 1-1 1-4 0-2.49 2.01-4.5 4.5-4.5s4.5 2.01 4.5 4.5c0 3 1 4 1 4H3.5z" stroke="currentColor" strokeWidth="1.2" strokeLinejoin="round"/></svg>);
const IconLink = () => (<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M6.5 9.5l3-3M5.5 7L4 8.5a2.83 2.83 0 004 4L9.5 11M10.5 9l1.5-1.5a2.83 2.83 0 00-4-4L6.5 5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/></svg>);
const IconTrash = () => (<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3 4.5h10M6 4.5V3a1 1 0 011-1h2a1 1 0 011 1v1.5" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/><path d="M4 4.5l.7 8.5a1 1 0 001 .9h4.6a1 1 0 001-.9l.7-8.5" stroke="currentColor" strokeWidth="1.1"/></svg>);
const IconEdit = () => (<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M9.5 3.5l3 3M3 10.5l6.5-6.5 3 3L6 13.5H3v-3z" stroke="currentColor" strokeWidth="1.1" strokeLinejoin="round"/></svg>);
const IconBack = () => (<svg width="10" height="16" viewBox="0 0 10 16" fill="none"><path d="M8.5 1.5L2 8l6.5 6.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/></svg>);
const IconPerson = () => (<svg width="14" height="14" viewBox="0 0 14 14" fill="none"><circle cx="7" cy="4.5" r="2.5" stroke="currentColor" strokeWidth="1.1"/><path d="M2.5 13c0-2.49 2.01-4.5 4.5-4.5s4.5 2.01 4.5 4.5" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/></svg>);
const IconPlus = () => (<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M10 4V16M4 10H16" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/></svg>);
const IconGlobe = () => (<svg width="18" height="18" viewBox="0 0 18 18" fill="none"><circle cx="9" cy="9" r="7" stroke="currentColor" strokeWidth="1.2"/><ellipse cx="9" cy="9" rx="3.5" ry="7" stroke="currentColor" strokeWidth="1.1"/><path d="M2.5 6.5h13M2.5 11.5h13" stroke="currentColor" strokeWidth="1.1"/></svg>);
const IconRepeat = () => (<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M11.5 1.5L14 4l-2.5 2.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/><path d="M2 7.5V7a3 3 0 013-3h9" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/><path d="M4.5 14.5L2 12l2.5-2.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/><path d="M14 8.5V9a3 3 0 01-3 3H2" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/></svg>);

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
  const [confirmDelete, setConfirmDelete] = useState(null);
  const [toast, setToast] = useState(null);
  const [newSpaceName, setNewSpaceName] = useState("");
  const [newEvent, setNewEvent] = useState({ title: "", date: "", time: "", repeat: "none" });
  const [lang, setLang] = useState("ru");

  const t = I18N[lang];

  const formatRelativeDate = (dateStr) => {
    const d = new Date(dateStr + "T00:00:00");
    const today = new Date("2026-03-28T00:00:00");
    const diff = Math.round((d - today) / 86400000);
    if (diff === 0) return t.today;
    if (diff === 1) return t.tomorrow;
    if (diff === 2) return t.dayAfter;
    return `${d.getDate()} ${t.months[d.getMonth()]}`;
  };

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
    spaces: t.spaces, spaceCreate: t.newSpace, spaceDetail: selectedSpace?.name || "",
    spaceEdit: t.edit, members: t.members, eventCreate: t.newEvent,
    eventDetail: t.event, reminders: t.reminders, language: t.language,
  };

  const space = selectedSpace;
  const isAdmin = space?.role === "admin";

  const Header = ({ title, right }) => (
    <div style={{ height: 56, display: "flex", alignItems: "center", padding: "0 4px", borderBottom: "0.5px solid #e5e5e5", background: "#fff", position: "sticky", top: 0, zIndex: 10, flexShrink: 0 }}>
      {screen !== "spaces" && (
        <button onClick={goBack} style={{ width: 44, height: 44, display: "flex", alignItems: "center", justifyContent: "center", background: "none", border: "none", cursor: "pointer", color: "#378ADD" }}><IconBack /></button>
      )}
      <span style={{ flex: 1, fontSize: 17, fontWeight: 600, paddingLeft: screen === "spaces" ? 16 : 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{title}</span>
      {right}
    </div>
  );

  const ListItem = ({ left, title, subtitle, right, onClick }) => (
    <button onClick={onClick} style={{ display: "flex", alignItems: "center", gap: 12, padding: "14px 16px", width: "100%", background: "none", border: "none", cursor: onClick ? "pointer" : "default", textAlign: "left", fontSize: 15 }}>
      {left}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontWeight: 500, color: "#1a1a1a", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{title}</div>
        {subtitle && <div style={{ fontSize: 13, color: "#8e8e93", marginTop: 2 }}>{subtitle}</div>}
      </div>
      {right}
    </button>
  );

  const Avatar = ({ name, size = 42, id = 0 }) => (
    <div style={{ width: size, height: size, borderRadius: "50%", background: colorFor(id), display: "flex", alignItems: "center", justifyContent: "center", color: "#fff", fontSize: size * 0.35, fontWeight: 600, flexShrink: 0, letterSpacing: 0.5 }}>{initials(name)}</div>
  );

  const Section = ({ title, children }) => (
    <div style={{ marginBottom: 8 }}>
      {title && <div style={{ fontSize: 12, fontWeight: 600, color: "#8e8e93", textTransform: "uppercase", letterSpacing: 0.8, padding: "20px 16px 8px" }}>{title}</div>}
      <div style={{ background: "#fff", borderTop: "0.5px solid #e5e5e5", borderBottom: "0.5px solid #e5e5e5" }}>{children}</div>
    </div>
  );

  const Divider = () => <div style={{ height: 0.5, background: "#e5e5e5", marginLeft: 70 }} />;

  const Toggle = ({ on, onToggle }) => (
    <button onClick={onToggle} style={{ width: 48, height: 28, borderRadius: 14, padding: 2, background: on ? "#1D9E75" : "#e5e5e5", border: "none", cursor: "pointer", transition: "background 0.2s", flexShrink: 0 }}>
      <div style={{ width: 24, height: 24, borderRadius: 12, background: "#fff", transition: "transform 0.2s", transform: on ? "translateX(20px)" : "translateX(0)", boxShadow: "0 1px 3px rgba(0,0,0,0.15)" }} />
    </button>
  );

  const ActionButton = ({ icon, label, color = "#378ADD", onClick }) => (
    <button onClick={onClick} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6, background: "none", border: "none", cursor: "pointer", padding: "8px 4px", minWidth: 64 }}>
      <div style={{ width: 44, height: 44, borderRadius: 12, background: color + "14", display: "flex", alignItems: "center", justifyContent: "center", color }}>{icon}</div>
      <span style={{ fontSize: 11, color, fontWeight: 500 }}>{label}</span>
    </button>
  );

  const SettingsIcon = ({ bg, color, children }) => (
    <div style={{ width: 42, height: 42, borderRadius: 12, background: bg, display: "flex", alignItems: "center", justifyContent: "center", color }}>{children}</div>
  );

  const RepeatPicker = ({ value, onChange }) => {
    const [open, setOpen] = useState(false);
    const opts = Object.entries(t.repeatOptions);
    const current = t.repeatOptions[value] || t.repeatOptions.none;
    return (
      <div>
        <div style={{ height: 0.5, background: "#e5e5e5", marginLeft: 16 }} />
        <button onClick={() => setOpen(!open)} style={{
          display: "flex", alignItems: "center", width: "100%", padding: "13px 16px",
          background: "none", border: "none", cursor: "pointer", textAlign: "left", fontSize: 15, gap: 10,
        }}>
          <div style={{ color: value && value !== "none" ? "#7F77DD" : "#8e8e93" }}><IconRepeat /></div>
          <span style={{ flex: 1, color: "#1a1a1a" }}>{t.repeat}</span>
          <span style={{ fontSize: 14, color: value && value !== "none" ? "#7F77DD" : "#8e8e93", fontWeight: value && value !== "none" ? 500 : 400 }}>{current}</span>
          <svg width="10" height="6" viewBox="0 0 10 6" fill="none" style={{ transform: open ? "rotate(180deg)" : "none", transition: "transform 0.2s", marginLeft: 2 }}>
            <path d="M1 1l4 4 4-4" stroke="#999" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
        {open && (
          <div style={{ borderTop: "0.5px solid #e5e5e5" }}>
            {opts.map(([key, label], i) => (
              <div key={key}>
                {i > 0 && <div style={{ height: 0.5, background: "#e5e5e5", marginLeft: 44 }} />}
                <button onClick={() => { onChange(key); setOpen(false); }} style={{
                  display: "flex", alignItems: "center", width: "100%", padding: "11px 16px 11px 44px",
                  background: key === value || (key === "none" && !value) ? "#f2f2f7" : "none",
                  border: "none", cursor: "pointer", textAlign: "left", fontSize: 14,
                }}>
                  <span style={{ flex: 1, fontWeight: key === value || (key === "none" && !value) ? 600 : 400 }}>{label}</span>
                  {(key === value || (key === "none" && !value)) && (
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                      <path d="M3 8.5l3 3L13 4" stroke="#378ADD" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  )}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  // ─── Screens ───

  const renderSpaces = () => (
    <div style={{ background: "#f2f2f7", minHeight: "100%" }}>
      <Section>
        {spaces.map((s, i) => (
          <div key={s.id}>
            {i > 0 && <Divider />}
            <ListItem left={<Avatar name={s.name} id={s.id} />} title={s.name}
              subtitle={`${s.membersCount} ${t.membersUnit} · ${s.eventsCount} ${t.eventsUnit}`}
              right={<ChevronRight />} onClick={() => navigate("spaceDetail", { space: s })} />
          </div>
        ))}
      </Section>
      <Section title={t.settings}>
        <ListItem left={<SettingsIcon bg="#BA751714" color="#BA7517"><IconBell /></SettingsIcon>}
          title={t.reminders} subtitle={t.reminderSubtitle} right={<ChevronRight />} onClick={() => navigate("reminders")} />
        <Divider />
        <ListItem left={<SettingsIcon bg="#378ADD14" color="#378ADD"><IconGlobe /></SettingsIcon>}
          title={t.language} subtitle={t.langName} right={<ChevronRight />} onClick={() => navigate("language")} />
      </Section>
    </div>
  );

  const renderSpaceDetail = () => {
    const spaceEvents = events[space.id] || [];
    return (
      <div style={{ background: "#f2f2f7", minHeight: "100%" }}>
        <div style={{ display: "flex", justifyContent: "center", gap: 12, padding: "16px 16px 8px", background: "#fff", borderBottom: "0.5px solid #e5e5e5" }}>
          {isAdmin && <ActionButton icon={<IconEdit />} label={t.editAction} onClick={() => { setEditingSpaceName(space.name); navigate("spaceEdit"); }} />}
          <ActionButton icon={<IconPeople />} label={t.membersAction} onClick={() => navigate("members")} />
          <ActionButton icon={<IconLink />} label={t.linkAction} color="#7F77DD" onClick={() => showToast(t.linkCopied)} />
          {isAdmin && <ActionButton icon={<IconTrash />} label={t.deleteAction} color="#E24B4A" onClick={() => setConfirmDelete("space")} />}
        </div>

        {confirmDelete === "space" && (
          <div style={{ margin: 16, padding: 16, background: "#FCEBEB", borderRadius: 12 }}>
            <div style={{ fontSize: 14, fontWeight: 500, color: "#A32D2D", marginBottom: 12 }}>{t.deleteSpaceConfirm(space.name)}</div>
            <div style={{ display: "flex", gap: 8 }}>
              <button onClick={() => { setSpaces(s => s.filter(x => x.id !== space.id)); setHistory([]); setScreen("spaces"); showToast(t.spaceDeleted); }}
                style={{ flex: 1, padding: "10px 0", borderRadius: 10, border: "none", background: "#E24B4A", color: "#fff", fontWeight: 600, fontSize: 14, cursor: "pointer" }}>{t.deleteBtn}</button>
              <button onClick={() => setConfirmDelete(null)}
                style={{ flex: 1, padding: "10px 0", borderRadius: 10, border: "0.5px solid #ddd", background: "#fff", color: "#1a1a1a", fontWeight: 500, fontSize: 14, cursor: "pointer" }}>{t.cancelBtn}</button>
            </div>
          </div>
        )}

        <Section title={`${t.eventsTitle} · ${spaceEvents.length}`}>
          {spaceEvents.length === 0 ? (
            <div style={{ padding: "32px 16px", textAlign: "center", color: "#8e8e93", fontSize: 14 }}>{t.noEvents}</div>
          ) : spaceEvents.map((ev, i) => (
            <div key={ev.id}>
              {i > 0 && <Divider />}
              <ListItem
                left={<div style={{ width: 42, height: 48, borderRadius: 10, background: "#f2f2f7", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", border: "0.5px solid #e5e5e5" }}>
                  <span style={{ fontSize: 16, fontWeight: 600, lineHeight: 1.1 }}>{new Date(ev.date + "T00:00:00").getDate()}</span>
                  <span style={{ fontSize: 10, color: "#8e8e93", textTransform: "uppercase", fontWeight: 500 }}>{t.months[new Date(ev.date + "T00:00:00").getMonth()]}</span>
                </div>}
                title={ev.title}
                subtitle={`${formatRelativeDate(ev.date)}${ev.time ? ` · ${ev.time}` : ""}${ev.repeat ? ` · ${t.repeatOptions[ev.repeat]}` : ""} · ${ev.author}`}
                right={<ChevronRight />}
                onClick={() => { setEditingEvent({ ...ev }); navigate("eventDetail", { event: ev }); }}
              />
            </div>
          ))}
        </Section>

        <button onClick={() => { setNewEvent({ title: "", date: "", time: "", repeat: "none" }); navigate("eventCreate"); }}
          style={{ position: "absolute", bottom: 24, right: 20, width: 52, height: 52, borderRadius: 26, background: "#378ADD", border: "none", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 4px 12px rgba(55,138,221,0.35)" }}>
          <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M11 5V17M5 11H17" stroke="#fff" strokeWidth="2.2" strokeLinecap="round"/></svg>
        </button>
      </div>
    );
  };

  const renderSpaceEdit = () => (
    <div style={{ background: "#f2f2f7", minHeight: "100%" }}>
      <Section title={t.spaceName}>
        <div style={{ padding: "8px 16px 12px" }}>
          <input value={editingSpaceName} onChange={e => setEditingSpaceName(e.target.value)}
            style={{ width: "100%", padding: "12px 14px", fontSize: 16, borderRadius: 10, border: "0.5px solid #d1d1d6", outline: "none", background: "#fff", boxSizing: "border-box" }}
            placeholder={t.namePlaceholder} autoFocus />
        </div>
      </Section>
      <div style={{ padding: "12px 16px" }}>
        <button onClick={() => { setSpaces(s => s.map(x => x.id === space.id ? { ...x, name: editingSpaceName } : x)); setSelectedSpace({ ...space, name: editingSpaceName }); goBack(); showToast(t.saved); }}
          style={{ width: "100%", padding: "14px 0", borderRadius: 12, border: "none", background: "#378ADD", color: "#fff", fontSize: 16, fontWeight: 600, cursor: "pointer", opacity: editingSpaceName.trim() ? 1 : 0.4 }}
          disabled={!editingSpaceName.trim()}>{t.save}</button>
      </div>
    </div>
  );

  const renderMembers = () => {
    const members = MOCK.members[space?.id] || [];
    return (
      <div style={{ background: "#f2f2f7", minHeight: "100%" }}>
        <Section title={t.membersCount(members.length)}>
          {members.map((m, i) => (
            <div key={m.id}>
              {i > 0 && <Divider />}
              <ListItem left={<Avatar name={m.name} size={38} id={m.id} />} title={m.name}
                subtitle={`@${m.username}${m.role === "admin" ? ` · ${t.administrator}` : ""}`}
                right={isAdmin && m.role !== "admin" ? (
                  <button onClick={(e) => { e.stopPropagation(); setConfirmDelete(m.id); }}
                    style={{ padding: "5px 12px", borderRadius: 8, border: "0.5px solid #E24B4A33", background: "#FCEBEB", color: "#E24B4A", fontSize: 12, fontWeight: 600, cursor: "pointer" }}>{t.removeMember}</button>
                ) : m.role === "admin" ? (
                  <span style={{ fontSize: 11, color: "#7F77DD", background: "#EEEDFE", padding: "3px 10px", borderRadius: 6, fontWeight: 600 }}>admin</span>
                ) : null}
              />
              {confirmDelete === m.id && (
                <div style={{ padding: "8px 16px 12px 70px" }}>
                  <div style={{ padding: 12, background: "#FCEBEB", borderRadius: 10, fontSize: 13 }}>
                    <span style={{ color: "#A32D2D" }}>{t.removeMemberConfirm(m.name)}</span>
                    <div style={{ display: "flex", gap: 8, marginTop: 10 }}>
                      <button onClick={() => { setConfirmDelete(null); showToast(t.memberRemoved(m.name)); }}
                        style={{ padding: "7px 16px", borderRadius: 8, border: "none", background: "#E24B4A", color: "#fff", fontSize: 12, fontWeight: 600, cursor: "pointer" }}>{t.yesRemove}</button>
                      <button onClick={() => setConfirmDelete(null)}
                        style={{ padding: "7px 16px", borderRadius: 8, border: "0.5px solid #ddd", background: "#fff", fontSize: 12, cursor: "pointer" }}>{t.cancelBtn}</button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </Section>
        <div style={{ padding: 16, fontSize: 13, color: "#8e8e93", textAlign: "center", lineHeight: 1.5 }}>{t.membersInviteHint}</div>
      </div>
    );
  };

  const renderEventDetail = () => {
    const ev = editingEvent;
    if (!ev) return null;
    return (
      <div style={{ background: "#f2f2f7", minHeight: "100%" }}>
        <Section title={t.eventDetails}>
          <div style={{ padding: "12px 16px" }}>
            <label style={{ fontSize: 12, color: "#8e8e93", fontWeight: 500, display: "block", marginBottom: 6 }}>{t.title}</label>
            <input value={ev.title} onChange={e => setEditingEvent({ ...ev, title: e.target.value })}
              style={{ width: "100%", padding: "11px 14px", fontSize: 16, borderRadius: 10, border: "0.5px solid #d1d1d6", outline: "none", background: "#fff", boxSizing: "border-box" }} />
          </div>
          <div style={{ height: 0.5, background: "#e5e5e5", marginLeft: 16 }} />
          <div style={{ padding: "12px 16px", display: "flex", gap: 12 }}>
            <div style={{ flex: 1 }}>
              <label style={{ fontSize: 12, color: "#8e8e93", fontWeight: 500, display: "block", marginBottom: 6 }}>{t.date}</label>
              <input type="date" value={ev.date} onChange={e => setEditingEvent({ ...ev, date: e.target.value })}
                style={{ width: "100%", padding: "11px 14px", fontSize: 15, borderRadius: 10, border: "0.5px solid #d1d1d6", outline: "none", background: "#fff", boxSizing: "border-box" }} />
            </div>
            <div style={{ flex: 1 }}>
              <label style={{ fontSize: 12, color: "#8e8e93", fontWeight: 500, display: "block", marginBottom: 6 }}>{t.time}</label>
              <input type="time" value={ev.time || ""} onChange={e => setEditingEvent({ ...ev, time: e.target.value || null })}
                style={{ width: "100%", padding: "11px 14px", fontSize: 15, borderRadius: 10, border: "0.5px solid #d1d1d6", outline: "none", background: "#fff", boxSizing: "border-box" }} />
            </div>
          </div>
          <RepeatPicker value={ev.repeat || "none"} onChange={(v) => setEditingEvent({ ...ev, repeat: v === "none" ? null : v })} />
        </Section>
        <Section>
          <div style={{ padding: "12px 16px", display: "flex", alignItems: "center", gap: 10, color: "#8e8e93" }}>
            <IconPerson /><span style={{ fontSize: 14 }}>{t.createdBy}: {ev.author}</span>
          </div>
        </Section>
        <div style={{ padding: "12px 16px" }}>
          <button onClick={() => { setEvents(evs => ({ ...evs, [ev.spaceId]: evs[ev.spaceId].map(x => x.id === ev.id ? editingEvent : x) })); goBack(); showToast(t.eventUpdated); }}
            style={{ width: "100%", padding: "14px 0", borderRadius: 12, border: "none", background: "#378ADD", color: "#fff", fontSize: 16, fontWeight: 600, cursor: "pointer" }}>{t.save}</button>
        </div>
        <div style={{ padding: "0 16px" }}>
          <button onClick={() => setConfirmDelete("event")}
            style={{ width: "100%", padding: "14px 0", borderRadius: 12, border: "0.5px solid #E24B4A33", background: "#FCEBEB", color: "#E24B4A", fontSize: 15, fontWeight: 600, cursor: "pointer" }}>{t.deleteEvent}</button>
        </div>
        {confirmDelete === "event" && (
          <div style={{ margin: 16, padding: 16, background: "#FCEBEB", borderRadius: 12 }}>
            <div style={{ fontSize: 14, fontWeight: 500, color: "#A32D2D", marginBottom: 12 }}>{t.deleteEventConfirm(ev.title)}</div>
            <div style={{ display: "flex", gap: 8 }}>
              <button onClick={() => { setEvents(evs => ({ ...evs, [ev.spaceId]: evs[ev.spaceId].filter(x => x.id !== ev.id) })); goBack(); showToast(t.eventDeleted); }}
                style={{ flex: 1, padding: "10px 0", borderRadius: 10, border: "none", background: "#E24B4A", color: "#fff", fontWeight: 600, fontSize: 14, cursor: "pointer" }}>{t.deleteBtn}</button>
              <button onClick={() => setConfirmDelete(null)}
                style={{ flex: 1, padding: "10px 0", borderRadius: 10, border: "0.5px solid #ddd", background: "#fff", fontSize: 14, cursor: "pointer" }}>{t.cancelBtn}</button>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderReminders = () => (
    <div style={{ background: "#f2f2f7", minHeight: "100%" }}>
      <Section title={t.reminderIntervals}>
        {Object.entries(t.reminderLabels).map(([key, label], i) => (
          <div key={key}>
            {i > 0 && <div style={{ height: 0.5, background: "#e5e5e5", marginLeft: 16 }} />}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 16px" }}>
              <span style={{ fontSize: 15 }}>{label}</span>
              <Toggle on={reminders[key]} onToggle={() => setReminders(r => ({ ...r, [key]: !r[key] }))} />
            </div>
          </div>
        ))}
      </Section>
      <div style={{ padding: "8px 16px", fontSize: 13, color: "#8e8e93", lineHeight: 1.5 }}>{t.reminderHint}</div>
    </div>
  );

  const renderLanguage = () => (
    <div style={{ background: "#f2f2f7", minHeight: "100%" }}>
      <Section title={t.interfaceLang}>
        {[["ru", "Русский"], ["en", "English"]].map(([code, label], i) => (
          <div key={code}>
            {i > 0 && <div style={{ height: 0.5, background: "#e5e5e5", marginLeft: 16 }} />}
            <button onClick={() => setLang(code)} style={{
              display: "flex", alignItems: "center", width: "100%", padding: "14px 16px",
              background: "none", border: "none", cursor: "pointer", textAlign: "left", fontSize: 15,
            }}>
              <span style={{ flex: 1, fontWeight: code === lang ? 600 : 400 }}>{label}</span>
              {code === lang && (
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                  <path d="M4 9.5l3.5 3.5L14 5" stroke="#378ADD" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              )}
            </button>
          </div>
        ))}
      </Section>
    </div>
  );

  const renderSpaceCreate = () => (
    <div style={{ background: "#f2f2f7", minHeight: "100%" }}>
      <Section title={t.spaceNameLabel}>
        <div style={{ padding: "8px 16px 12px" }}>
          <input value={newSpaceName} onChange={e => setNewSpaceName(e.target.value)}
            style={{ width: "100%", padding: "12px 14px", fontSize: 16, borderRadius: 10, border: "0.5px solid #d1d1d6", outline: "none", background: "#fff", boxSizing: "border-box" }}
            placeholder={t.spaceNamePlaceholder} autoFocus />
        </div>
      </Section>
      <div style={{ padding: "12px 16px" }}>
        <button onClick={() => {
          const id = Date.now();
          const newSpace = { id, name: newSpaceName.trim(), membersCount: 1, eventsCount: 0, inviteCode: Math.random().toString(36).slice(2, 10), role: "admin" };
          setSpaces(s => [...s, newSpace]);
          setEvents(evs => ({ ...evs, [id]: [] }));
          setHistory([]); setScreen("spaces"); showToast(t.spaceCreated);
        }} style={{ width: "100%", padding: "14px 0", borderRadius: 12, border: "none", background: "#378ADD", color: "#fff", fontSize: 16, fontWeight: 600, cursor: "pointer", opacity: newSpaceName.trim() ? 1 : 0.4 }}
          disabled={!newSpaceName.trim()}>{t.create}</button>
      </div>
      <div style={{ padding: "8px 16px", fontSize: 13, color: "#8e8e93", lineHeight: 1.5 }}>{t.spaceCreateHint}</div>
    </div>
  );

  const renderEventCreate = () => {
    const canSave = newEvent.title.trim() && newEvent.date;
    return (
      <div style={{ background: "#f2f2f7", minHeight: "100%" }}>
        <Section title={t.eventDetails}>
          <div style={{ padding: "12px 16px" }}>
            <label style={{ fontSize: 12, color: "#8e8e93", fontWeight: 500, display: "block", marginBottom: 6 }}>{t.title}</label>
            <input value={newEvent.title} onChange={e => setNewEvent(ev => ({ ...ev, title: e.target.value }))}
              style={{ width: "100%", padding: "11px 14px", fontSize: 16, borderRadius: 10, border: "0.5px solid #d1d1d6", outline: "none", background: "#fff", boxSizing: "border-box" }}
              placeholder={t.eventTitlePlaceholder} autoFocus />
          </div>
          <div style={{ height: 0.5, background: "#e5e5e5", marginLeft: 16 }} />
          <div style={{ padding: "12px 16px", display: "flex", gap: 12 }}>
            <div style={{ flex: 1 }}>
              <label style={{ fontSize: 12, color: "#8e8e93", fontWeight: 500, display: "block", marginBottom: 6 }}>{t.date}</label>
              <input type="date" value={newEvent.date} onChange={e => setNewEvent(ev => ({ ...ev, date: e.target.value }))}
                style={{ width: "100%", padding: "11px 14px", fontSize: 15, borderRadius: 10, border: "0.5px solid #d1d1d6", outline: "none", background: "#fff", boxSizing: "border-box" }} />
            </div>
            <div style={{ flex: 1 }}>
              <label style={{ fontSize: 12, color: "#8e8e93", fontWeight: 500, display: "block", marginBottom: 6 }}>{t.time} <span style={{ color: "#b0b0b0" }}>{t.timeOptional}</span></label>
              <input type="time" value={newEvent.time} onChange={e => setNewEvent(ev => ({ ...ev, time: e.target.value }))}
                style={{ width: "100%", padding: "11px 14px", fontSize: 15, borderRadius: 10, border: "0.5px solid #d1d1d6", outline: "none", background: "#fff", boxSizing: "border-box" }} />
            </div>
          </div>
          <RepeatPicker value={newEvent.repeat} onChange={(v) => setNewEvent(ev => ({ ...ev, repeat: v }))} />
        </Section>
        <div style={{ padding: "12px 16px" }}>
          <button onClick={() => {
            const ev = { id: Date.now(), title: newEvent.title.trim(), date: newEvent.date, time: newEvent.time || null, repeat: newEvent.repeat === "none" ? null : newEvent.repeat, author: "Иван", spaceId: space.id };
            setEvents(evs => ({ ...evs, [space.id]: [...(evs[space.id] || []), ev].sort((a, b) => a.date.localeCompare(b.date)) }));
            goBack(); showToast(t.eventCreated);
          }} style={{ width: "100%", padding: "14px 0", borderRadius: 12, border: "none", background: "#378ADD", color: "#fff", fontSize: 16, fontWeight: 600, cursor: "pointer", opacity: canSave ? 1 : 0.4 }}
            disabled={!canSave}>{t.createEvent}</button>
        </div>
        <div style={{ padding: "8px 16px", fontSize: 13, color: "#8e8e93", lineHeight: 1.5 }}>{t.eventCreateHint(space?.name)}</div>
      </div>
    );
  };

  const screens = {
    spaces: renderSpaces, spaceCreate: renderSpaceCreate, spaceDetail: renderSpaceDetail,
    spaceEdit: renderSpaceEdit, members: renderMembers, eventCreate: renderEventCreate,
    eventDetail: renderEventDetail, reminders: renderReminders, language: renderLanguage,
  };

  return (
    <div style={{ display: "flex", justifyContent: "center", padding: 0 }}>
      <div style={{ width: 375, minHeight: 700, background: "#f2f2f7", borderRadius: 20, overflow: "hidden", border: "0.5px solid #d1d1d6", display: "flex", flexDirection: "column", boxShadow: "0 4px 24px rgba(0,0,0,0.08)", position: "relative" }}>
        <Header title={headerTitle[screen]}
          right={screen === "spaces" ? (
            <button onClick={() => { setNewSpaceName(""); navigate("spaceCreate"); }}
              style={{ width: 44, height: 44, display: "flex", alignItems: "center", justifyContent: "center", background: "none", border: "none", cursor: "pointer", color: "#378ADD", marginRight: 4 }}><IconPlus /></button>
          ) : null}
        />
        <div style={{ flex: 1, overflowY: "auto" }}>{screens[screen]?.()}</div>
        {toast && (
          <div style={{ position: "absolute", bottom: 32, left: "50%", transform: "translateX(-50%)", background: "#1a1a1a", color: "#fff", padding: "10px 20px", borderRadius: 20, fontSize: 14, fontWeight: 500, whiteSpace: "nowrap", animation: "fadeInUp 0.2s ease" }}>
            {toast}
          </div>
        )}
      </div>
      <style>{`
        @keyframes fadeInUp { from { opacity: 0; transform: translateX(-50%) translateY(8px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }
        input[type="date"], input[type="time"] { -webkit-appearance: none; font-family: inherit; }
      `}</style>
    </div>
  );
}
