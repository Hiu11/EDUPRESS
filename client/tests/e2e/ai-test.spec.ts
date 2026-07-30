import { test, expect } from '@playwright/test';
import { PlaywrightAgent } from '@midscene/web/playwright';

test.describe('Autonomous AI E2E Tester (Midscene.js)', () => {
  test('AI should autonomously test the core booking/learning flow', async ({ page }) => {
    // 1. Setup AI Agent
    const ai = new PlaywrightAgent(page);
    
    // 2. Đi tới trang chủ EduPress
    await page.goto('/');

    // 3. Yêu cầu AI tự động "nhìn" giao diện và tương tác
    // Thay vì viết selector cứng (như .btn-primary), AI sẽ dùng LLM Vision để tìm nút
    await ai.aiAction('Click on the "Bắt đầu học ngay" or "Khám phá" button on the hero section');
    
    // 4. AI tự động kiểm tra xem danh sách khoá học có tải thành công không
    const hasCourses = await ai.aiQuery('Are there any course cards visible on the screen? Reply with boolean true/false');
    expect(hasCourses).toBe(true);

    // 5. AI tự động bấm vào một khoá học bất kỳ
    await ai.aiAction('Click on the first course card title to view details');
    
    // 6. Test Real-time Comments UI (Issue #22)
    await ai.aiAction('Scroll down to the "Real-time Discussion" or "Thảo luận trực tiếp" section');
    const hasCommentInput = await ai.aiAssert('There should be an input field to write a comment');
    
    // 7. Nhập thử comment bằng AI
    await ai.aiAction('Type "Bài học rất hay, test bằng AI" into the comment input field and click "Gửi bình luận"');
    
    // 8. Đảm bảo UI không bị vỡ sau khi comment
    await ai.aiAssert('The comment "Bài học rất hay, test bằng AI" should appear in the comment list with a "Vừa xong" badge');
  });
});
