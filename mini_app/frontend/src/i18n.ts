import { createContext, useContext } from 'react'

export type Language = 'ru' | 'en'

export const translations = {
  ru: {
    // Spaces page
    spaces: 'Пространства',
    newSpace: 'Новое пространство',
    settings: 'Настройки',
    membersUnit: 'участн.',
    emptySpaces: 'Нет пространств. Нажми + чтобы создать первое.',
    createSpaceAriaLabel: 'Создать пространство',

    // Settings items
    reminders: 'Напоминания',
    reminderSubtitle: 'Настроить интервалы',
    language: 'Язык',
    langName: 'Русский',

    // Reminder settings
    reminderIntervals: 'Интервалы напоминаний',
    reminderHint: 'Настройки применяются ко всем новым событиям во всех пространствах. Уже созданные напоминания не изменятся.',
    reminderLabels: {
      '1d': 'За 1 день',
      '2h': 'За 2 часа',
      '1h': 'За 1 час',
      '30m': 'За 30 минут',
      '15m': 'За 15 минут',
      '0m': 'В момент события',
    } as Record<string, string>,

    // Language settings
    interfaceLang: 'Язык интерфейса',

    // Space detail
    editAction: 'Изменить',
    membersAction: 'Участники',
    linkAction: 'Ссылка',
    deleteAction: 'Удалить',
    linkCopied: 'Ссылка скопирована',
    deleteSpaceConfirm: 'Удалить «{name}»? Все события и напоминания будут потеряны.',
    deleteBtn: 'Удалить',
    cancelBtn: 'Отмена',
    spaceDeleted: 'Пространство удалено',
    noEvents: 'Нет предстоящих событий',
    eventsTitle: 'События',

    // Space edit
    spaceName: 'Название пространства',
    namePlaceholder: 'Название',
    save: 'Сохранить',
    saved: 'Сохранено',

    // Members
    members: 'Участники',
    membersCount: '{n} участников',
    administrator: 'администратор',
    removeMember: 'Удалить',
    removeMemberConfirm: 'Удалить {name} из пространства?',
    yesRemove: 'Да, удалить',
    memberRemoved: '{name} удалён',
    membersInviteHint: 'Новые участники присоединяются по invite-ссылке пространства',

    // Event detail
    eventDetails: 'Детали события',
    title: 'Название',
    date: 'Дата',
    time: 'Время',
    createdBy: 'Создал',
    eventUpdated: 'Событие обновлено',
    deleteEvent: 'Удалить событие',
    deleteEventConfirm: 'Удалить «{title}»? Напоминания тоже будут удалены.',
    eventDeleted: 'Событие удалено',

    // Space create
    spaceNameLabel: 'Название пространства',
    spaceNamePlaceholder: 'Например, «Семья» или «Работа»',
    create: 'Создать',
    spaceCreated: 'Пространство создано',
    spaceCreateHint: 'Вы станете администратором. Пригласите участников по ссылке после создания.',

    // Event create
    event: 'Событие',
    newEvent: 'Новое событие',
    eventTitlePlaceholder: 'Ужин с друзьями',
    timeOptional: '(необязательно)',
    createEvent: 'Создать событие',
    eventCreated: 'Событие создано',
    eventCreateHint: 'Все участники пространства «{name}» получат уведомление о новом событии.',
    titleRequired: 'Название обязательно',
    titleTooLong: 'Название слишком длинное',
    dateRequired: 'Дата обязательна',
    pastDate: 'Выбранная дата уже прошла',

    // Relative dates
    today: 'сегодня',
    tomorrow: 'завтра',
    dayAfter: 'послезавтра',
    months: ['янв', 'фев', 'мар', 'апр', 'мая', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек'],
    monthsGenitive: ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'],
    weekdaysAccusative: ['в воскресенье', 'в понедельник', 'во вторник', 'в среду', 'в четверг', 'в пятницу', 'в субботу'],
    allDay: 'весь день',

    // State views
    loading: 'Загрузка...',
    errorTitle: 'Ошибка',
    errorDefault: 'Произошла ошибка',
    retry: 'Повторить',
    loadError: 'Не удалось загрузить',

    // Edit page
    edit: 'Редактировать',
    saving: 'Сохранение...',
    creating: 'Создание...',
    deleting: 'Удаление...',
    editing: 'Редактирование',
    spaceNotFound: 'Пространство не найдено',
    loadErrorGeneric: 'Не удалось загрузить данные',
    deleteError: 'Не удалось удалить',
    saveError: 'Не удалось сохранить',
    createError: 'Не удалось создать пространство',
    loadEventError: 'Не удалось загрузить событие',
    createEventError: 'Не удалось создать событие',
    titleTooLongDetail: 'Название слишком длинное (макс. 500 символов)',
    conflictWarning: 'На близкое время уже есть события:',
    eventCreateHintGeneric: 'Все участники пространства получат уведомление о новом событии.',
  },
  en: {
    spaces: 'Spaces',
    newSpace: 'New space',
    settings: 'Settings',
    membersUnit: 'members',
    emptySpaces: 'No spaces. Tap + to create your first.',
    createSpaceAriaLabel: 'Create space',

    reminders: 'Reminders',
    reminderSubtitle: 'Set up intervals',
    language: 'Language',
    langName: 'English',

    reminderIntervals: 'Reminder intervals',
    reminderHint: 'Settings apply to all new events across all spaces. Existing reminders won\'t change.',
    reminderLabels: {
      '1d': '1 day before',
      '2h': '2 hours before',
      '1h': '1 hour before',
      '30m': '30 min before',
      '15m': '15 min before',
      '0m': 'At the time of event',
    } as Record<string, string>,

    interfaceLang: 'Interface language',

    editAction: 'Edit',
    membersAction: 'Members',
    linkAction: 'Link',
    deleteAction: 'Delete',
    linkCopied: 'Link copied',
    deleteSpaceConfirm: 'Delete "{name}"? All events and reminders will be lost.',
    deleteBtn: 'Delete',
    cancelBtn: 'Cancel',
    spaceDeleted: 'Space deleted',
    noEvents: 'No upcoming events',
    eventsTitle: 'Events',

    spaceName: 'Space name',
    namePlaceholder: 'Name',
    save: 'Save',
    saved: 'Saved',

    members: 'Members',
    membersCount: '{n} members',
    administrator: 'administrator',
    removeMember: 'Remove',
    removeMemberConfirm: 'Remove {name} from the space?',
    yesRemove: 'Yes, remove',
    memberRemoved: '{name} removed',
    membersInviteHint: 'New members join via the space invite link',

    eventDetails: 'Event details',
    title: 'Title',
    date: 'Date',
    time: 'Time',
    createdBy: 'Created by',
    eventUpdated: 'Event updated',
    deleteEvent: 'Delete event',
    deleteEventConfirm: 'Delete "{title}"? Reminders will also be removed.',
    eventDeleted: 'Event deleted',

    spaceNameLabel: 'Space name',
    spaceNamePlaceholder: 'E.g. "Family" or "Work"',
    create: 'Create',
    spaceCreated: 'Space created',
    spaceCreateHint: 'You\'ll become the admin. Invite members via link after creation.',

    event: 'Event',
    newEvent: 'New event',
    eventTitlePlaceholder: 'Dinner with friends',
    timeOptional: '(optional)',
    createEvent: 'Create event',
    eventCreated: 'Event created',
    eventCreateHint: 'All members of "{name}" will be notified about the new event.',
    titleRequired: 'Title is required',
    titleTooLong: 'Title is too long',
    dateRequired: 'Date is required',
    pastDate: 'Selected date is in the past',

    today: 'today',
    tomorrow: 'tomorrow',
    dayAfter: 'day after tomorrow',
    months: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    monthsGenitive: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
    weekdaysAccusative: ['on Sunday', 'on Monday', 'on Tuesday', 'on Wednesday', 'on Thursday', 'on Friday', 'on Saturday'],
    allDay: 'all day',

    loading: 'Loading...',
    errorTitle: 'Error',
    errorDefault: 'An error occurred',
    retry: 'Retry',
    loadError: 'Failed to load',

    edit: 'Edit',
    saving: 'Saving...',
    creating: 'Creating...',
    deleting: 'Deleting...',
    editing: 'Editing',
    spaceNotFound: 'Space not found',
    loadErrorGeneric: 'Failed to load data',
    deleteError: 'Failed to delete',
    saveError: 'Failed to save',
    createError: 'Failed to create space',
    loadEventError: 'Failed to load event',
    createEventError: 'Failed to create event',
    titleTooLongDetail: 'Title is too long (max 500 characters)',
    conflictWarning: 'There are events at a nearby time:',
    eventCreateHintGeneric: 'All space members will be notified about the new event.',
  },
} as const

export type Translations = typeof translations.ru | typeof translations.en

export interface I18nContextType {
  t: Translations
  language: Language
  setLanguage: (lang: Language) => void
}

export const I18nContext = createContext<I18nContextType>({
  t: translations.ru,
  language: 'ru',
  setLanguage: () => {},
})

export function useTranslation(): I18nContextType {
  return useContext(I18nContext)
}
