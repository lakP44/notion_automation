require("dotenv").config();
const { google } = require("googleapis");
const fetch = require("node-fetch");

// 환경 변수 로드
const {
  GOOGLE_DRIVE_CLIENT_ID,
  GOOGLE_DRIVE_CLIENT_SECRET,
  GOOGLE_DRIVE_REFRESH_TOKEN,
  GOOGLE_DRIVE_FOLDER_ID,
  NOTION_TOKEN,
  NOTION_PAGE_ID,
} = process.env;

// Google OAuth 설정
const oauth2Client = new google.auth.OAuth2(
  GOOGLE_DRIVE_CLIENT_ID,
  GOOGLE_DRIVE_CLIENT_SECRET
);
oauth2Client.setCredentials({ refresh_token: GOOGLE_DRIVE_REFRESH_TOKEN });

const drive = google.drive({ version: "v3", auth: oauth2Client });

(async () => {
  try {
    // 구글 드라이브 폴더 내 이미지 파일 가져오기
    const res = await drive.files.list({
      q: `'${GOOGLE_DRIVE_FOLDER_ID}' in parents and mimeType contains 'image/' and trashed = false`,
      fields: "files(id, name, mimeType, webContentLink)",
    });

    const files = res.data.files;
    if (!files.length) throw new Error("📂 폴더에 이미지가 없습니다.");

    // 랜덤으로 하나 선택
    const selected = files[Math.floor(Math.random() * files.length)];
    const imageUrl = `https://drive.google.com/uc?export=download&id=${selected.id}`;

    // Notion 페이지 커버 업데이트
    const notionRes = await fetch(`https://api.notion.com/v1/pages/${NOTION_PAGE_ID}`, {
      method: "patch",
      headers: {
        "Authorization": `Bearer ${NOTION_TOKEN}`,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
      },
      body: JSON.stringify({
        cover: {
          type: "external",
          external: {
            url: imageUrl
          }
        }
      })
    });

    if (!notionRes.ok) throw new Error("🛑 Notion 커버 변경 실패");

    console.log(`✅ 커버 이미지 변경 완료: ${imageUrl}`);
  } catch (err) {
    console.error("❌ 오류 발생:", err.message);
  }
})();
