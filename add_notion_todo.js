const { Client } = require("@notionhq/client");
require("dotenv").config();

const notion = new Client({ auth: process.env.NOTION_TOKEN });

// 데이터베이스에 페이지 추가하기
(async () => {
  // console.log("Using DB ID:", process.env.NOTION_DB_ID);
  try {
    const response = await notion.pages.create({
      parent: {
        database_id: process.env.NOTION_DB_ID,
      },
      properties: {
        이름: { title: [ { text: { content: `Test Todo - ${new Date().toISOString()}`, } } ] },
        완료: { checkbox: true },
        상태: { status: { name: "진행 중" } },
      },
    });

    console.log("✅ Page created:", response.id);
  } catch (error) {
    console.error("❌ Error:", error);
  }
})();
