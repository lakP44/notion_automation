require("dotenv").config();
const { Client } = require("@notionhq/client");
const { google } = require("googleapis");

// .env에서 가져올 값들
const {
  NOTION_TOKEN,
  GOOGLE_DRIVE_CLIENT_ID,
  GOOGLE_DRIVE_CLIENT_SECRET,
  GOOGLE_DRIVE_REFRESH_TOKEN,
  GOOGLE_DRIVE_FOLDER_ID,
  TARGET_BLOCK_ID,
  PARENT_PAGE_ID
} = process.env;

// Notion 클라이언트
const notion = new Client({ auth: NOTION_TOKEN });

// Google Drive 클라이언트
const oauth2Client = new google.auth.OAuth2(
  GOOGLE_DRIVE_CLIENT_ID,
  GOOGLE_DRIVE_CLIENT_SECRET
);
oauth2Client.setCredentials({ refresh_token: GOOGLE_DRIVE_REFRESH_TOKEN });
const drive = google.drive({ version: "v3", auth: oauth2Client });

(async () => {
  try {
    // Step 1: 기존 블록 삭제
    await notion.blocks.delete({ block_id: TARGET_BLOCK_ID });
    console.log("🗑 블록 삭제 완료:", TARGET_BLOCK_ID);

    // Step 2: Google Drive 이미지 중 랜덤 선택
    const res = await drive.files.list({
      q: `'${GOOGLE_DRIVE_FOLDER_ID}' in parents and mimeType contains 'image/' and trashed = false`,
      fields: "files(id, name)",
    });

    const files = res.data.files;
    if (!files.length) throw new Error("📁 폴더에 이미지 없음");

    const selected = files[Math.floor(Math.random() * files.length)];
    const imageUrl = `https://drive.google.com/uc?export=download&id=${selected.id}`;

    // Step 3: 새 embed 블록 추가 (페이지 맨 아래에 들어감)
    await notion.blocks.children.append({
      block_id: PARENT_PAGE_ID,
      children: [
        {
          object: "block",
          type: "embed",
          embed: { url: imageUrl },
        },
      ],
    });

    console.log("✅ 새 이미지 embed 추가됨:", imageUrl);
  } catch (err) {
    console.error("❌ 오류:", err.message);
  }
})();
