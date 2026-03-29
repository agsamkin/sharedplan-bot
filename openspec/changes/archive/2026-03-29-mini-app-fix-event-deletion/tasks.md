## 1. Исправление API-клиента

- [x] 1.1 В `mini_app/frontend/src/api/client.ts` в функции `request()` перенести установку заголовка `Content-Type: application/json` внутрь блока `if (body !== undefined)`, чтобы он не отправлялся для DELETE-запросов без тела

## 2. Исправление страницы события

- [x] 2.1 В `mini_app/frontend/src/pages/EventDetailPage.tsx` добавить state `spaceId` (string | null) и сохранять `event.space_id` из ответа `getEvent` в `fetchEvent`
- [x] 2.2 Добавить state `deleting` (boolean) для отслеживания процесса удаления
- [x] 2.3 В `handleDelete` установить `deleting = true` перед вызовом API и `deleting = false` при ошибке
- [x] 2.4 В `handleDelete` заменить `navigate(-1)` на `navigate('/spaces/' + spaceId, { replace: true })` для надёжной навигации после удаления
- [x] 2.5 В `handleDelete` добавить вызов `showToast(message)` в блоке `catch` для отображения ошибки через toast
- [x] 2.6 Передать `confirmText={deleting ? 'Удаление...' : 'Удалить'}` в `ConfirmInline` и заблокировать кнопку подтверждения во время удаления

## 3. Проверка

- [x] 3.1 Убедиться, что `deleteSpace` и `removeMember` (используют ту же функцию `del()`) продолжают работать корректно без `Content-Type`
- [x] 3.2 Проверить, что после удаления события пользователь видит актуальный список событий на странице пространства
