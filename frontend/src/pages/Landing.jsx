import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import './Landing.css'

function Landing() {
  const { user } = useAuth()
  const isLoggedIn = !!user

  const featureCards = [
    { icon: '🎒', title: 'Всё в одном месте', desc: 'Билеты, бронирования, планы поездок — не надо переключаться между разными приложениями.' },
    { icon: '🔔', title: 'Не забудете ни о чём', desc: 'Напоминания о рейсах, заселении и экскурсиях — придут вовремя.' },
    { icon: '📊', title: 'Считаем вашу статистику', desc: 'Сколько стран посетили, сколько городов увидели — всё видно в профиле.' },
    { icon: '🤖', title: 'ИИ-помощник', desc: 'Можно спросить совета по поездке — бот подскажет что посмотреть и куда сходить.' },
    { icon: '📎', title: 'Прикрепить документы', desc: 'Загрузите билет или бронь — система сама вытащит нужные данные из файла.' },
    { icon: '✈', title: 'Отслеживание рейсов', desc: 'Если рейс задержат или отменят — вы узнаете первыми.' },
  ]

  const galleryItems = [
    { src: 'https://images.unsplash.com/photo-1506929562872-bb421503ef21?w=600&h=400&fit=crop', label: 'Бали, Индонезия' },
    { src: 'https://images.unsplash.com/photo-1499856871958-5b9627545d1a?w=600&h=400&fit=crop', label: 'Париж, Франция' },
    { src: 'https://images.unsplash.com/photo-1536098561742-ca998e48cbcc?w=600&h=400&fit=crop', label: 'Токио, Япония' },
    { src: 'https://images.unsplash.com/photo-1516483638261-f4dbaf036963?w=600&h=400&fit=crop', label: 'Амстердам, Нидерланды' },
    { src: 'https://images.unsplash.com/photo-1512100356356-de1b84283e18?w=600&h=400&fit=crop', label: 'Рим, Италия' },
    { src: 'https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=600&h=400&fit=crop', label: 'Швейцарские Альпы' },
  ]

  return (
    <div className="landing">
      <section className="hero">
        <div className="hero-overlay" />
        <div className="hero-content container">
          <h1 className="hero-title">
            Все путешествия <br />
            <span className="hero-accent">в одном месте</span>
          </h1>
          <p className="hero-subtitle">
            Билеты, жильё, планы и напоминания — TripHelper собирает всё,
            чтобы вы могли наслаждаться путешествием, а не искать нужную информацию.
          </p>
          <div className="hero-actions">
            {isLoggedIn ? (
              <Link to="/dashboard" className="btn btn-primary btn-lg">
                Мои поездки
              </Link>
            ) : (
              <>
                <Link to="/register" className="btn btn-primary btn-lg">
                  Начать путешествовать
                </Link>
                <Link to="/login" className="btn btn-secondary btn-lg">
                  Уже есть аккаунт
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      <section className="features container">
        <h2 className="section-title">Почему TripHelper?</h2>
        <p className="section-subtitle">Всё, что нужно путешественнику, в одном сервисе</p>
        <div className="features-grid">
          {featureCards.map((card, i) => (
            <div className="feature-card" key={i}>
              <div className="feature-icon">{card.icon}</div>
              <h3>{card.title}</h3>
              <p>{card.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="gallery">
        <h2 className="section-title">Мир ждёт вас</h2>
        <div className="gallery-scroll">
          {galleryItems.map((item, i) => (
            <div className="gallery-item" key={i}>
              <img src={item.src} alt={item.label} />
              <div className="gallery-item-overlay">
                <span>{item.label}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="cta-section">
        <div className="container cta-content">
          <h2>Готовы к следующему приключению?</h2>
          <p>Присоединяйтесь к TripHelper и планируйте путешествия без хаоса</p>
          <Link to="/register" className="btn btn-primary btn-lg">
            Создать аккаунт
          </Link>
        </div>
      </section>

      <footer className="footer">
        <div className="container footer-inner">
          <div className="footer-logo">
            ✈ TripHelper
          </div>
          <p className="footer-text">&copy; 2026 TripHelper. Будыгин Тимофей.</p>
        </div>
      </footer>
    </div>
  )
}

export default Landing
