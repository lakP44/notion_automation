const { Client } = require("@notionhq/client");
require("dotenv").config();

const notion = new Client({ auth: process.env.NOTION_TOKEN });

async function GetDBPageTest(dbId) {
  const pageTitle = "맨몸 운동"; // 검색할 제목

  const response = await notion.databases.query({
    database_id: dbId,
    filter: {
      property: "이름", // 제목 필드 이름 (예: "이름", "제목", "Name")
      title: {
        equals: pageTitle,
      },
    },
    sorts: [
      {
        timestamp: "created_time",
        direction: "descending",
      },
    ],
    page_size: 1,
  });

  const latestPage = response.results[0];
  if (!latestPage) {
    console.log("❌ 해당 제목의 페이지 없음");
    return 0;
  }

  console.log("📄 최신 페이지 ID:", latestPage.id);
  console.log("📆 생성일:", latestPage.created_time);

  // 여기에 다른 동작(예: 복사, 이동, 수정 등) 추가 가능
  return 1; // 예시: 이동한 일정 개수 1개로 간주
}

module.exports = GetDBPageTest;
