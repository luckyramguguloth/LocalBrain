import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const body = await req.json();
    
    // Secure Server-Side Proxy:
    // This hides the FastAPI backend URL (http://127.0.0.1:8000) from the browser.
    // Hackers cannot inspect the network tab to find our internal APIs.
    const response = await fetch('http://127.0.0.1:8000/api/v1/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    const data = await response.json();
    
    // Create strict response, ensuring no sensitive headers are leaked
    return NextResponse.json(data, {
      status: 200,
      headers: {
        'Strict-Transport-Security': 'max-age=63072000; includeSubDomains; preload',
      }
    });
  } catch (error) {
    console.error('Secure Proxy Error:', error);
    return NextResponse.json(
      { error: 'Secure backend proxy failed.' },
      { status: 500 }
    );
  }
}
