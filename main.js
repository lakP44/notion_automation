// 최초 진입점입니다.
const fetchWeeklyStats = require("./notion/fetchWeeklyStats");
const shiftTasksToNextDay = require("./notion/shiftTasksToNextDay");
require("dotenv").config();

(async () => {
  const dbId = process.env.NOTION_DB_ID;

  console.log("🟡 주간 일정 개수 계산 중...");
  const count = await fetchWeeklyStats(dbId);
  console.log(`📅 이번 주 일정 수: ${count}개`);

  console.log("🟠 미완료 일정 다음날로 이동 중...");
  const moved = await shiftTasksToNextDay(dbId);
  console.log(`📦 이동된 일정 수: ${moved}개`);

  console.log("✅ 모든 작업 완료");
})();
