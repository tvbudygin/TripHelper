import { useEffect, useRef } from 'react'
import worldMapSvg from '../data/world-map.svg?raw'
import { COUNTRY_NAME_TO_ISO, normalizeCountryName } from '../data/countries.js'
import './WorldMap.css'

/** Карта мира: страны из списка закрашиваются зелёным. Карта: simple-world-map (Al MacDonald, Fritz Lekschas) */
function WorldMap({ visitedCountryNames }) {
  const containerRef = useRef(null)

  useEffect(() => {
    const visitedCodes = new Set(
      visitedCountryNames
        .map((name) => COUNTRY_NAME_TO_ISO[normalizeCountryName(name)])
        .filter(Boolean),
    )
    containerRef.current.querySelectorAll('path[id], g[id]').forEach((element) => {
      element.classList.toggle('world-map-visited', visitedCodes.has(element.id))
    })
  }, [visitedCountryNames])

  return (
    <div className="world-map" ref={containerRef} dangerouslySetInnerHTML={{ __html: worldMapSvg }} />
  )
}

export default WorldMap
