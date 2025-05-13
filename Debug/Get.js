const { Client } = require("@notionhq/client");
require("dotenv").config();

const notion = new Client({ auth: process.env.NOTION_TOKEN });
const databaseId = process.env.NOTION_DB_ID;

async function fetchAllPages() {
  const pages = [];
  let cursor = undefined;

  while (true) {
    const response = await notion.databases.query({
      database_id: databaseId,
      start_cursor: cursor,
    });

    pages.push(...response.results);

    if (!response.has_more) break;
    cursor = response.next_cursor;
  }

  return pages;
}

// ✅ 실행 함수로 감싸서 await 사용
async function main() {
  const pages = await fetchAllPages();

  for (const page of pages) {
    console.log("📄 Page ID:", page.id);

    const props = page.properties;
    for (const [key, value] of Object.entries(props)) {
      let val = "";

      switch (value.type) {
        case "title":
          val = value.title.map(t => t.plain_text).join("");
          break;
        case "rich_text":
          val = value.rich_text.map(t => t.plain_text).join("");
          break;
        case "checkbox":
          val = value.checkbox;
          break;
        case "select":
          val = value.select?.name || "";
          break;
        case "multi_select":
          val = value.multi_select.map(s => s.name).join(", ");
          break;
        case "status":
          val = value.status?.name || "";
          break;
        case "number":
          val = value.number;
          break;
        case "date":
          val = value.date?.start || "";
          break;
        default:
          val = `[${value.type}] 타입 처리 안됨`;
      }

      console.log(`  🔹 ${key}: ${val}`);
    }

    console.log("----");
  }
}

main().catch(console.error);
