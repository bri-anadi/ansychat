# 💬 Dokumentasi Aplikasi Ansychat - Chat Real-time

## 🛠️ Tech Stack
Aplikasi chat ini dibangun menggunakan teknologi:

| Teknologi | Deskripsi |
|-----------|-----------|
| 🐍 **Python Flask** | Framework web yang ringan dan fleksibel untuk backend |
| 🔌 **Flask-SocketIO** | Implementasi WebSocket untuk komunikasi real-time |
| 🗄️ **SQLAlchemy** | ORM untuk manajemen database |
| 🔑 **Flask-JWT-Extended** | Sistem autentikasi berbasis token |
| 📚 **Swagger UI** | Dokumentasi API interaktif |
| 💾 **SQLite** | Database ringan untuk penyimpanan data |

## 📁 Struktur Proyek
```
chat-app/
├── 🔧 config.py           # Konfigurasi aplikasi
├── ⚠️ exceptions.py       # Definisi exception
├── 📊 models.py          # Model database
├── 🛠️ services.py        # Business logic
├── 📡 socketio_handlers.py # Handler Socket.IO
├── 🛣️ routes.py          # Route API
├── 🚀 main.py           # Entry point aplikasi
├── 📂 static/
|       📄 swagger.yaml   # Dokumentasi API
└── 📂 templates/
    └── 📄 index.html   # Tampilan Frontend
```

## 🔄 Alur Aplikasi

### 1. 🔐 Sistem Autentikasi dan Manajemen Pengguna

#### Alur Proses:
1. ✍️ Pengguna input username
2. 🔍 Sistem cek ketersediaan (`/api/check-username`)
3. 💡 Jika terpakai, sistem beri saran alternatif
4. 🎫 Login via `/api/login`
5. 🔑 Sistem berikan JWT token

📝 **Contoh Kode Check Username:**
```python
import requests

response = requests.post('http://localhost:5000/api/check-username', 
    json={'username': 'john_doe'})
print(response.json())
```

### 2. 📨 Manajemen Pesan

#### Fitur Utama:
- 📥 **Read**: GET `/api/messages`
- ✏️ **Create**: Event 'new_message'
- 📝 **Update**: Event 'edit_message'
- 🗑️ **Delete**: Event 'delete_message'

📝 **Contoh Pengiriman Pesan:**
```python
socketio.emit('new_message', {
    'token': 'jwt_token_here',
    'username': 'john_doe',
    'content': 'Halo semua!'
})
```

### 3. ⚡ Komunikasi Real-time

#### Event Socket.IO:
| Event | Fungsi |
|-------|--------|
| 🚪 `join` | Bergabung ke chat room |
| 🚶 `leave` | Keluar dari chat room |
| 📝 `new_message` | Kirim pesan baru |
| ✏️ `edit_message` | Edit pesan |
| 🗑️ `delete_message` | Hapus pesan |

### 4. ⚠️ Penanganan Error

#### Jenis Error:
- 👤 `UserNotFoundException`
- 🚫 `UnauthorizedAccessException`
- 💬 `MessageNotFoundException`
- ❌ `ValidationError`

### 5. 🗄️ Struktur Database

#### Tabel User 👤
| Field | Tipe | Deskripsi |
|-------|------|-----------|
| id | INT | Primary key |
| username | STRING | Nama pengguna (unik) |
| is_online | BOOLEAN | Status online |

#### Tabel Message 💬
| Field | Tipe | Deskripsi |
|-------|------|-----------|
| id | INT | Primary key |
| user_id | INT | Foreign key ke User |
| username | STRING | Nama pengguna |
| content | TEXT | Isi pesan |
| timestamp | DATETIME | Waktu kirim |

### 6. 🛠️ Layanan Pendukung

#### UserService 👥
- ✅ Cek username
- 💡 Generate saran username
- 🟢 Kelola status online

#### MessageService 💬
- 📜 Ambil riwayat pesan
- ✅ Validasi pesan
- 🔄 Edit & hapus pesan
- 🔍 Cari pesan

## 📡 Penggunaan API

### 🔑 Endpoint Autentikasi

```http
POST /api/check-username
Content-Type: application/json

{
    "username": "john_doe"
}
```

```http
POST /api/login
Content-Type: application/json

{
    "username": "john_doe"
}
```

### 💬 Endpoint Pesan

```http
GET /api/messages
Authorization: Bearer <jwt_token>
```

### ⚡ Events Socket.IO

📝 **Bergabung ke chat:**
```javascript
socket.emit('join', {
    username: 'john_doe'
});
```

📝 **Kirim pesan:**
```javascript
socket.emit('new_message', {
    token: 'jwt_token',
    username: 'john_doe',
    content: 'Halo semua!'
});
```

## 🔒 Keamanan
1. 🔑 JWT token authentication
2. ✅ Input validation
3. 🛡️ Message ownership authorization
4. 🚫 Unauthorized access protection
5. 🧹 XSS prevention

## 🔮 Pengembangan Selanjutnya

| Fitur | Deskripsi |
|-------|-----------|
| 🔐 Autentikasi | Sistem login yang lebih kuat |
| 📁 Upload File | Dukungan berbagi file |
| 🏠 Chat Rooms | Implementasi ruang chat |
| 🔔 Notifikasi | Sistem notifikasi push |
| 💾 Backup | Pencadangan database otomatis |

---
📚 **Catatan**: Dokumentasi ini akan terus diperbarui sesuai perkembangan aplikasi.
