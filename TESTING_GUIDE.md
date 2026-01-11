# 🧪 HƯỚNG DẪN KIỂM TRA REAL-TIME WEBSOCKET

## 🎯 MỤC TIÊU

Verify rằng WebSocket real-time updates đang hoạt động chính xác sau khi fix event names mismatch.

---

## 📋 CHUẨN BỊ

### Đã có sẵn:
- ✅ Backend đang chạy (port 5000)
- ✅ Frontend đang serve (port 8080)
- ✅ Event names đã fix matching
- ✅ Debug logging đã thêm
- ✅ Test page đã tạo

---

## 🔬 CÁC TEST CASES

### Test 1: WebSocket Connection
**Mục tiêu:** Verify connection giữa client và server

**Steps:**
1. Mở test page: http://localhost:8080/test-websocket.html
2. Quan sát status box ở đầu page

**Expected Results:**
- ✅ Status hiển thị "✅ Đã kết nối - Real-time active" (màu xanh)
- ✅ Logs hiển thị "✅ WebSocket connected successfully!"
- ✅ Logs hiển thị "✅ Server confirmed: Connected to anomaly detection system"

**If Failed:**
- ❌ Status: "❌ Mất kết nối" (màu đỏ)
- ❌ Logs: "❌ Connection error: ..."
- **Action:** Check backend running, check CORS, check Socket.IO version

---

### Test 2: Traffic Update Events (2 giây interval)
**Mục tiêu:** Verify traffic updates đang được emit mỗi 2 giây

**Steps:**
1. Đợi 10 giây sau khi kết nối
2. Quan sát "🚦 Traffic Update" box

**Expected Results:**
- ✅ Counter tăng từ 0 → ~5 sau 10 giây
- ✅ Timestamp update liên tục
- ✅ Logs hiển thị: "🚦 TRAFFIC UPDATE: X connections, Y bytes sent"

**Calculation:**
- 10 seconds / 2 second interval = 5 events
- Acceptable range: 4-6 events

**If Failed:**
- Counter = 0 → Backend không emit hoặc event name sai
- **Action:** Check backend terminal for "📡 Emitting traffic_update"

---

### Test 3: Anomaly Detection Events (Random 10-30s)
**Mục tiêu:** Verify anomaly events đang được emit randomly

**Steps:**
1. Đợi 60 giây
2. Quan sát "📊 Anomaly Detected" box

**Expected Results:**
- ✅ Counter tăng 1-4 lần trong 60 giây
- ✅ Logs hiển thị: "📊 ANOMALY DETECTED: [type] from [IP] - Severity: [level]"
- ✅ Types: Suspicious Traffic, SQL Injection, DoS Attack, XSS Attack, Unauthorized Access

**Statistics:**
- Backend emit every 10-30s (random)
- 70% chance to emit (30% skip)
- Expected in 60s: 2-4 events

**If Failed:**
- Counter = 0 after 60s → Very unlikely but possible (bad luck)
- **Action:** Wait another 30s, should see at least 1

---

### Test 4: Alert Created Events (High/Critical only)
**Mục tiêu:** Verify alerts tạo khi có anomaly severity cao

**Steps:**
1. Đợi cho anomaly events xuất hiện
2. Quan sát "🚨 Alert Created" box

**Expected Results:**
- ✅ Counter tăng khi anomaly có severity = 'high' hoặc 'critical'
- ✅ Logs hiển thị: "🚨 ALERT CREATED: [title] - [severity] severity"
- ✅ Alert count ≤ Anomaly count (chỉ high/critical alerts)

**Calculation:**
- ~25% anomalies are high severity
- ~25% anomalies are critical severity
- ~50% anomalies = high/critical → alert created
- If 4 anomalies detected → expect ~2 alerts

**If Failed:**
- No alerts despite anomalies → Check severity distribution
- **Action:** Check backend code line 113-133 in monitoring_service.py

---

### Test 5: Dashboard Integration
**Mục tiêu:** Verify dashboard nhận real-time updates

**Steps:**
1. Mở dashboard: http://localhost:8080/index.html
2. Mở DevTools (F12) → Console tab
3. Để dashboard mở trong 30 giây
4. **KHÔNG reload page!**

**Expected Results:**
- ✅ Console: "✅ WebSocket connected successfully"
- ✅ Console: "✅ Server confirmed: ..."
- ✅ Console: "Traffic update: ..." (mỗi 2 giây)
- ✅ Console: "New anomaly detected: ..." (random)
- ✅ Anomalies table tự động thêm rows mới
- ✅ Metrics (Total Anomalies count) tự động tăng
- ✅ Notifications xuất hiện khi có anomaly

**Critical:**
- ❌ **KHÔNG CẦN** nhấn F5 refresh!
- ❌ **KHÔNG CẦN** click reload button!
- ✅ Data tự động update trong background

**If Failed:**
- No console logs → WebSocket không connect
- Console logs OK nhưng table không update → Event handlers có vấn đề
- **Action:** Check main.js lines 48-61 (event handlers)

---

### Test 6: Multiple Tabs (Broadcast Test)
**Mục tiêu:** Verify events broadcast đến tất cả clients

**Steps:**
1. Mở test page: http://localhost:8080/test-websocket.html (Tab 1)
2. Mở test page lần 2: http://localhost:8080/test-websocket.html (Tab 2)
3. Đợi 20 giây
4. So sánh counters giữa 2 tabs

**Expected Results:**
- ✅ Cả 2 tabs có cùng connection status
- ✅ Cả 2 tabs có counters gần giống nhau (±1)
- ✅ Cả 2 tabs đều nhận events simultaneously

**If Failed:**
- Tab 1 OK, Tab 2 failed → Connection issue
- Different counters → Events không broadcast properly
- **Action:** Check socketio emit() vs emit() with broadcast=True

---

## 📊 EXPECTED METRICS (60 SECONDS TEST)

| Event Type | Expected Count | Interval | Notes |
|-----------|---------------|----------|-------|
| Traffic Update | ~30 | 2s | 60s / 2s = 30 events |
| Anomaly Detected | 2-4 | 10-30s random | 70% chance each interval |
| Alert Created | 1-2 | Conditional | Only high/critical anomalies |
| Model Updated | 0 | Manual only | Không tự động emit |

---

## 🐛 TROUBLESHOOTING

### Issue: "Connection Error"

**Symptoms:**
- Status box màu đỏ
- Logs: "❌ Connection error: ..."
- Counters = 0

**Solutions:**
1. Check backend running:
   ```powershell
   curl.exe http://127.0.0.1:5000/api/health
   ```

2. Check backend terminal có errors không

3. Check Socket.IO version mismatch:
   - Server: flask-socketio (check requirements.txt)
   - Client: Socket.IO 4.5.4 (check HTML)

4. Check CORS settings trong app.py

---

### Issue: "Connected nhưng không có Events"

**Symptoms:**
- Status box màu xanh "Đã kết nối"
- Logs có "WebSocket connected"
- Nhưng counters = 0 sau 30 giây

**Solutions:**
1. Check backend terminal có "📡 Emitting..." không
   - Có → Frontend event names sai
   - Không → Monitoring service không chạy

2. Verify event names:
   ```javascript
   // Frontend lắng nghe:
   socket.on('anomaly_detected', ...)
   socket.on('traffic_update', ...)
   socket.on('alert_created', ...)
   ```
   
   ```python
   # Backend emit:
   socketio_instance.emit('anomaly_detected', ...)
   socketio_instance.emit('traffic_update', ...)
   socketio_instance.emit('alert_created', ...)
   ```

3. Check monitoring service started:
   - Backend terminal should print "✅ Monitoring service started"

---

### Issue: "Dashboard không Auto-update"

**Symptoms:**
- Test page hoạt động tốt
- Dashboard console có logs
- Nhưng table/metrics không update

**Solutions:**
1. Check event handlers gọi đúng functions:
   ```javascript
   // main.js lines 48-61
   socket.on('anomaly_detected', (data) => {
       dashboardManager.loadAnomaliesTable();  // ← Check this
       dashboardManager.updateMetrics();
   });
   ```

2. Check dashboardManager đã khởi tạo chưa:
   - Console gõ: `dashboardManager`
   - Nếu undefined → Timing issue

3. Check page đang active:
   - Router có thể đã switch page
   - Event handlers chỉ work khi đúng page

---

## ✅ SUCCESS CRITERIA

### Minimum Requirements (MUST PASS):
- [x] Test page connect successfully
- [x] Traffic updates mỗi 2 giây
- [x] Ít nhất 1 anomaly trong 60 giây
- [x] Dashboard console có logs

### Optimal Performance (SHOULD PASS):
- [x] ~30 traffic updates trong 60 giây
- [x] 2-4 anomalies trong 60 giây
- [x] Alerts tạo cho high/critical anomalies
- [x] Dashboard table tự động update
- [x] Không cần manual refresh

### Excellent (BONUS):
- [x] Multiple tabs đều nhận events
- [x] Reconnect button hoạt động
- [x] Notifications hiển thị đúng
- [x] Charts update theo events

---

## 📝 TEST REPORT TEMPLATE

Copy template này để ghi lại kết quả test:

```
=== WEBSOCKET REAL-TIME TEST REPORT ===
Date: [DATE]
Tester: [NAME]

=== Test Results ===
✅/❌ Test 1 - WebSocket Connection: 
✅/❌ Test 2 - Traffic Updates (Expected: ~5 in 10s): 
✅/❌ Test 3 - Anomaly Detection (Expected: 2-4 in 60s): 
✅/❌ Test 4 - Alert Creation: 
✅/❌ Test 5 - Dashboard Integration: 
✅/❌ Test 6 - Multiple Tabs: 

=== Metrics (60 seconds) ===
Traffic Update Count: __ (Expected: ~30)
Anomaly Count: __ (Expected: 2-4)
Alert Count: __ (Expected: 1-2)

=== Issues Found ===
1. [Issue description]
2. [Issue description]

=== Conclusion ===
Overall Status: ✅ PASS / ❌ FAIL
Real-time working: YES / NO
Manual refresh needed: YES / NO

=== Notes ===
[Any additional observations]
```

---

## 🚀 NEXT ACTIONS

### If ALL tests PASS:
1. ✅ Close this testing phase
2. ✅ Update documentation
3. ✅ Move to Phase 2 (Authentication & Security)
4. ✅ Deploy to production environment

### If ANY test FAILS:
1. ⚠️ Review TROUBLESHOOTING section
2. ⚠️ Check backend terminal logs
3. ⚠️ Check browser DevTools console
4. ⚠️ Debug specific failing test
5. ⚠️ Re-run tests after fixes

---

**Happy Testing! 🎉**
