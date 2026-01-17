import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // 获取后端 URL（使用服务器端环境变量）
    let backendUrl = process.env.BACKEND_SERVICE_URL || 'http://localhost:8000';
    
    // Ensure URL has protocol (fix for Railway URLs without https://)
    if (backendUrl && !backendUrl.startsWith('http://') && !backendUrl.startsWith('https://')) {
      backendUrl = `https://${backendUrl}`;
    }
    
    console.log('📝 Generating scripts via backend:', backendUrl);
    
    // 调用后端脚本生成 API
    const response = await fetch(`${backendUrl}/api/v3/generate-scripts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Backend script generation error:', response.status, errorText);
      return NextResponse.json(
        { success: false, error: errorText || `Backend error (${response.status})` },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    console.log('✅ Scripts generated successfully:', data.count);
    
    return NextResponse.json(data);
  } catch (error: any) {
    console.error('❌ Script generation error:', error);
    return NextResponse.json(
      { success: false, error: error.message || 'Script generation failed' },
      { status: 500 }
    );
  }
}
