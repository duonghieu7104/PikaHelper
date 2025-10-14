@echo off
echo 🇻🇳 Vietnamese Text Processing Test
echo =====================================

echo.
echo 1. Testing embedding service health...
curl -X GET http://localhost:8001/health

echo.
echo.
echo 2. Testing Vietnamese text preprocessing...
curl -X POST http://localhost:8001/preprocess -H "Content-Type: text/plain" -d "Xin chào, tôi là trợ lý AI cho game PokeMMO"

echo.
echo.
echo 3. Testing Vietnamese embedding generation...
curl -X POST http://localhost:8001/embed -H "Content-Type: application/json" -d "{\"text\": \"Xin chào, tôi là trợ lý AI cho game PokeMMO\", \"chunk_id\": \"vietnamese_test_001\"}"

echo.
echo.
echo 4. Testing with different Vietnamese sentences...

set sentences[0]="Làm thế nào để tải game PokeMMO trên điện thoại?"
set sentences[1]="Hướng dẫn hoàn thành cốt truyện Pokemon Fire Red"
set sentences[2]="Cách kiếm tiền hiệu quả trong PokeMMO"
set sentences[3]="Xây dựng đội hình PvP mạnh nhất"

for /L %%i in (0,1,3) do (
    echo.
    echo Testing sentence %%i...
    curl -X POST http://localhost:8001/embed -H "Content-Type: application/json" -d "{\"text\": %sentences[%%i]%, \"chunk_id\": \"vietnamese_test_%%i\"}"
)

echo.
echo.
echo 🎉 Vietnamese embedding test completed!
echo Check the output above for results.
pause
