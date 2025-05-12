const { Client } = require('@notionhq/client');

const notion = new Client({ auth: process.env.NOTION_TOKEN });

(async () => {
  const response = await notion.pages.create({
    parent: { database_id: process.env.NOTION_DB_ID },
    properties: {
      Name: {
        title: [{ text: { content: `Todo @ ${new Date().toISOString()}` } }],
      },
      Status: {
        select: { name: "Not Started" }
      }
    }
  });
  console.log("Page created: ", response.id);
})();
