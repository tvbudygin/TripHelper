/** Достаёт текст ошибки из ответа backend */
export function getErrorMessage(error, fallbackMessage) {
  const detail = error?.response?.data?.detail

  if (typeof detail === 'string') {
    return detail
  }
  if (Array.isArray(detail)) {
    return detail[0].msg
  }
  return fallbackMessage
}
