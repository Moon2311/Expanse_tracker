export function getErrorMessage(err) {
  const d = err?.response?.data;
  if (!d) return err?.message || "Something went wrong.";
  if (typeof d === "string") return d;
  if (d.message) return d.message;
  if (d.detail) return String(d.detail);
  if (d.errors) {
    try {
      return JSON.stringify(d.errors);
    } catch {
      return "Validation error.";
    }
  }
  return "Request failed.";
}
