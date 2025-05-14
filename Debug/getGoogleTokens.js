require("dotenv").config();
const { google } = require("googleapis");
const readline = require("readline");

const CLIENT_ID = process.env.GOOGLE_DRIVE_CLIENT_ID;
const CLIENT_SECRET = process.env.GOOGLE_DRIVE_CLIENT_SECRET;
const REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob";

const oAuth2Client = new google.auth.OAuth2(
  CLIENT_ID,
  CLIENT_SECRET,
  REDIRECT_URI
);

const authUrl = oAuth2Client.generateAuthUrl({
  access_type: "offline",
  scope: ["https://www.googleapis.com/auth/drive.readonly"],
});

console.log("🔗 다음 링크를 브라우저에 붙여넣고 로그인하세요:\n");
console.log(authUrl);

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

rl.question("\n📥 인증 코드를 입력하세요: ", async (code) => {
  rl.close();
  try {
    const { tokens } = await oAuth2Client.getToken(code);
    console.log("\n✅ 다음 토큰들을 .env 또는 GitHub Secrets에 저장하세요:");
    console.log("GOOGLE_DRIVE_REFRESH_TOKEN=" + tokens.refresh_token);
    console.log("GOOGLE_DRIVE_ACCESS_TOKEN=" + tokens.access_token);
  } catch (error) {
    console.error("❌ 토큰 가져오기 실패:", error);
  }
});
