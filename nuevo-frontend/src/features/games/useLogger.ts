export function useLogger() {
  const logEvent = (payload: any) => {
    fetch('/api/logs', { method: 'POST', body: JSON.stringify(payload)})
  }
  return { logEvent }
}
