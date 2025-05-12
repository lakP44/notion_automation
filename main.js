// 최초 진입점입니다.
require("dotenv").config();
const GetDBPageTest = require("./notion/GetDBPageTest.js");


(async () => {
  const dbId = process.env.NOTION_DB_ID;

//   console.log("🟡 주간 일정 개수 계산 중...");
//   const count = await fetchWeeklyStats(dbId);
//   console.log(`📅 이번 주 일정 수: ${count}개`);

  console.log("🟠 DB 페이지 추출...");
  const moved = await GetDBPageTest(dbId);
  console.log(`📦 발견된 일정 수: ${moved}개`);

  console.log("✅ 모든 작업 완료");
})();
