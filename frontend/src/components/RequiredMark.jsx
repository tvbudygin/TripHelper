/** Маленькая звёздочка над обязательным полем - ставится в подписи (label) рядом с названием поля */
function RequiredMark() {
  return <sup className="required-mark" aria-hidden="true">*</sup>
}

export default RequiredMark
