/** Все страны поездки */
export function getTripCountries(trip) {
  return [trip.country, ...trip.extra_stops.map((stop) => stop.country)]
}

/** Маршрут одной строкой: Рим, Италия → Париж, Франция */
export function formatTripPlaces(trip) {
  const places = [{ city: trip.city, country: trip.country }, ...trip.extra_stops]
  return places.map((place) => (place.city ? `${place.city}, ${place.country}` : place.country)).join(' → ')
}
