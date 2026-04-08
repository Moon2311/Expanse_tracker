export function unwrap(resData) {
  if (
    resData &&
    typeof resData === "object" &&
    resData.success === true &&
    "data" in resData
  ) {
    return resData.data;
  }
  return resData;
}
