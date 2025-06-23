import requests
import logging
import json
import re
from datetime import datetime
from typing import Dict, Any, List
from app.config import Config
import time

def detect_content_type(text: str) -> str:
    """
    Mendeteksi jenis konten berdasarkan analisis teks.
    """
    text_lower = text.lower()
    
    # Keywords untuk berbagai jenis konten
    meeting_keywords = [
        'meeting', 'rapat', 'diskusi', 'presentasi', 'agenda', 'peserta', 
        'moderator', 'ketua', 'sekretaris', 'notulen', 'keputusan', 'action item',
        'deadline', 'timeline', 'follow up', 'next meeting', 'meeting berikutnya'
    ]
    
    document_keywords = [
        'dokumen', 'laporan', 'artikel', 'paper', 'research', 'studi', 'analisis',
        'penelitian', 'survey', 'data', 'statistik', 'hasil', 'kesimpulan'
    ]
    
    presentation_keywords = [
        'slide', 'presentasi', 'demo', 'pitch', 'proposal', 'overview',
        'introduction', 'background', 'objectives', 'conclusion'
    ]
    
    interview_keywords = [
        'interview', 'wawancara', 'pertanyaan', 'jawaban', 'responden',
        'interviewee', 'interviewer', 'question', 'answer', 'response'
    ]
    
    lecture_keywords = [
        'kuliah', 'lecture', 'materi', 'pembelajaran', 'education', 'training',
        'workshop', 'seminar', 'tutorial', 'course', 'lesson'
    ]
    
    youtube_keywords = [
        'youtube', 'video', 'channel', 'subscriber', 'view', 'like', 'comment',
        'upload', 'stream', 'live', 'podcast', 'vlog', 'tutorial', 'review',
        'unboxing', 'gaming', 'music', 'entertainment', 'content creator',
        'youtuber', 'streamer', 'influencer', 'viral', 'trending'
    ]
    
    # Hitung kemunculan keywords
    scores = {
        'meeting': sum(1 for keyword in meeting_keywords if keyword in text_lower),
        'document': sum(1 for keyword in document_keywords if keyword in text_lower),
        'presentation': sum(1 for keyword in presentation_keywords if keyword in text_lower),
        'interview': sum(1 for keyword in interview_keywords if keyword in text_lower),
        'lecture': sum(1 for keyword in lecture_keywords if keyword in text_lower),
        'youtube': sum(1 for keyword in youtube_keywords if keyword in text_lower)
    }
    
    # Deteksi berdasarkan pola kalimat
    if re.search(r'(selamat|good|hello|hi).*(pagi|siang|sore|malam)', text_lower):
        scores['meeting'] += 3
    
    if re.search(r'(pertanyaan|question).*\d+', text_lower):
        scores['interview'] += 2
    
    if re.search(r'(slide|slide\s+\d+)', text_lower):
        scores['presentation'] += 3
    
    if re.search(r'(bab|chapter|section)\s+\d+', text_lower):
        scores['document'] += 2
    
    # YouTube-specific patterns
    if re.search(r'(subscribe|like|comment|share)', text_lower):
        scores['youtube'] += 3
    
    if re.search(r'(welcome|hello|hi).*(channel|video)', text_lower):
        scores['youtube'] += 2
    
    if re.search(r'(don\'t forget|jangan lupa).*(subscribe|like)', text_lower):
        scores['youtube'] += 3
    
    if re.search(r'(thanks|terima kasih).*(watching|menonton)', text_lower):
        scores['youtube'] += 2
    
    # Return jenis dengan score tertinggi
    content_type = max(scores, key=scores.get)
    return content_type if scores[content_type] > 0 else 'general'

def create_meeting_summary_prompt(text: str) -> str:
    """
    Membuat prompt untuk meeting summarization.
    """
    return f"""
TUGAS: Buat ringkasan meeting yang profesional dan terstruktur dari transkripsi berikut.

PETUNJUK:
1. Identifikasi topik utama dan agenda meeting
2. Ekstrak poin-poin penting dan keputusan yang diambil
3. Catat action items dan tanggung jawab
4. Identifikasi timeline dan deadline yang disebutkan
5. Ringkas dalam format yang mudah dibaca

TRANSKRIPSI MEETING:
{text}

FORMAT OUTPUT (dalam JSON):
{{
    "meeting_info": {{
        "title": "Judul meeting berdasarkan konteks",
        "date": "Tanggal meeting jika disebutkan",
        "duration": "Perkiraan durasi berdasarkan transkripsi",
        "participants": ["Daftar peserta yang disebutkan"]
    }},
    "agenda": ["Daftar agenda yang dibahas"],
    "key_points": [
        {{
            "topic": "Topik yang dibahas",
            "summary": "Ringkasan poin penting",
            "decisions": ["Keputusan yang diambil"],
            "notes": "Catatan tambahan"
        }}
    ],
    "action_items": [
        {{
            "task": "Deskripsi tugas",
            "assignee": "Orang yang bertanggung jawab",
            "deadline": "Deadline jika disebutkan",
            "priority": "High/Medium/Low"
        }}
    ],
    "next_meeting": {{
        "scheduled": "Ya/Tidak",
        "date": "Tanggal jika dijadwalkan",
        "agenda": "Agenda untuk meeting berikutnya"
    }},
    "executive_summary": "Ringkasan eksekutif dalam 2-3 kalimat",
    "risk_issues": ["Masalah atau risiko yang diidentifikasi"],
    "success_metrics": ["Metrik keberhasilan yang disebutkan"]
}}

Pastikan output dalam format JSON yang valid dan lengkap.
"""

def create_document_summary_prompt(text: str) -> str:
    """
    Membuat prompt untuk document summarization.
    """
    return f"""
TUGAS: Buat ringkasan dokumen yang komprehensif dan terstruktur dari teks berikut.

PETUNJUK:
1. Identifikasi topik utama dan tujuan dokumen
2. Ekstrak poin-poin kunci dan temuan penting
3. Identifikasi metodologi dan data yang digunakan
4. Ringkas kesimpulan dan rekomendasi
5. Catat referensi dan sumber yang disebutkan

DOKUMEN:
{text}

FORMAT OUTPUT (dalam JSON):
{{
    "document_info": {{
        "title": "Judul dokumen berdasarkan konteks",
        "type": "Jenis dokumen (laporan/artikel/paper/dll)",
        "author": "Penulis jika disebutkan",
        "date": "Tanggal publikasi jika disebutkan"
    }},
    "executive_summary": "Ringkasan eksekutif dalam 2-3 kalimat",
    "objectives": ["Tujuan dan sasaran dokumen"],
    "methodology": {{
        "approach": "Pendekatan yang digunakan",
        "data_sources": ["Sumber data yang digunakan"],
        "tools": ["Tools atau metode analisis"]
    }},
    "key_findings": [
        {{
            "finding": "Temuan utama",
            "description": "Penjelasan detail",
            "significance": "Pentingnya temuan ini"
        }}
    ],
    "conclusions": ["Kesimpulan utama"],
    "recommendations": [
        {{
            "recommendation": "Rekomendasi",
            "priority": "High/Medium/Low",
            "implementation": "Cara implementasi"
        }}
    ],
    "references": ["Referensi yang disebutkan"],
    "limitations": ["Keterbatasan studi/dokumen"]
}}

Pastikan output dalam format JSON yang valid dan lengkap.
"""

def create_presentation_summary_prompt(text: str) -> str:
    """
    Membuat prompt untuk presentation summarization.
    """
    return f"""
TUGAS: Buat ringkasan presentasi yang terstruktur dari transkripsi berikut.

PETUNJUK:
1. Identifikasi topik dan tujuan presentasi
2. Ekstrak poin-poin utama dari setiap slide/section
3. Catat data dan statistik yang disajikan
4. Identifikasi kesimpulan dan call-to-action
5. Ringkas dalam format yang mudah dipahami

TRANSCRIPSI PRESENTASI:
{text}

FORMAT OUTPUT (dalam JSON):
{{
    "presentation_info": {{
        "title": "Judul presentasi",
        "presenter": "Pembicara jika disebutkan",
        "audience": "Target audience",
        "duration": "Durasi presentasi"
    }},
    "overview": "Ringkasan singkat presentasi",
    "objectives": ["Tujuan presentasi"],
    "key_sections": [
        {{
            "section": "Nama section/slide",
            "content": "Konten utama",
            "key_points": ["Poin-poin penting"],
            "data": ["Data/statistik yang disajikan"]
        }}
    ],
    "main_arguments": ["Argumen utama yang disampaikan"],
    "supporting_evidence": ["Bukti atau data pendukung"],
    "conclusions": ["Kesimpulan presentasi"],
    "call_to_action": "Aksi yang diharapkan dari audience",
    "q_and_a": ["Pertanyaan dan jawaban jika ada"]
}}

Pastikan output dalam format JSON yang valid dan lengkap.
"""

def create_interview_summary_prompt(text: str) -> str:
    """
    Membuat prompt untuk interview summarization.
    """
    return f"""
TUGAS: Buat ringkasan wawancara yang terstruktur dari transkripsi berikut.

PETUNJUK:
1. Identifikasi topik wawancara dan peserta
2. Ekstrak pertanyaan dan jawaban penting
3. Catat insight dan pengalaman yang dibagikan
4. Identifikasi rekomendasi dan saran
5. Ringkas dalam format yang informatif

TRANSCRIPSI WAWANCARA:
{text}

FORMAT OUTPUT (dalam JSON):
{{
    "interview_info": {{
        "topic": "Topik wawancara",
        "interviewee": "Nama responden",
        "interviewer": "Nama pewawancara",
        "date": "Tanggal wawancara jika disebutkan"
    }},
    "background": "Latar belakang responden",
    "key_questions": [
        {{
            "question": "Pertanyaan yang diajukan",
            "answer": "Jawaban responden",
            "insights": ["Insight yang diperoleh"]
        }}
    ],
    "main_themes": ["Tema utama yang dibahas"],
    "experiences": ["Pengalaman yang dibagikan"],
    "challenges": ["Tantangan yang dihadapi"],
    "solutions": ["Solusi yang disarankan"],
    "recommendations": ["Rekomendasi dari responden"],
    "key_learnings": ["Pelajaran yang dapat diambil"],
    "follow_up": ["Pertanyaan lanjutan yang mungkin relevan"]
}}

Pastikan output dalam format JSON yang valid dan lengkap.
"""

def create_lecture_summary_prompt(text: str) -> str:
    """
    Membuat prompt untuk lecture/training summarization.
    """
    return f"""
TUGAS: Buat ringkasan materi pembelajaran yang terstruktur dari transkripsi berikut.

PETUNJUK:
1. Identifikasi topik dan tujuan pembelajaran
2. Ekstrak konsep dan teori yang diajarkan
3. Catat contoh dan ilustrasi yang diberikan
4. Identifikasi poin-poin penting untuk diingat
5. Ringkas dalam format yang mudah dipelajari

MATERI PEMBELAJARAN:
{text}

FORMAT OUTPUT (dalam JSON):
{{
    "lecture_info": {{
        "title": "Judul materi",
        "instructor": "Pengajar/pembicara",
        "subject": "Mata pelajaran/topik",
        "level": "Level kesulitan (Basic/Intermediate/Advanced)"
    }},
    "learning_objectives": ["Tujuan pembelajaran"],
    "main_concepts": [
        {{
            "concept": "Konsep utama",
            "explanation": "Penjelasan detail",
            "examples": ["Contoh yang diberikan"],
            "importance": "Mengapa penting"
        }}
    ],
    "key_theories": ["Teori yang diajarkan"],
    "practical_applications": ["Aplikasi praktis"],
    "important_points": ["Poin-poin penting untuk diingat"],
    "common_mistakes": ["Kesalahan umum yang dihindari"],
    "tips_and_tricks": ["Tips dan trik"],
    "exercises": ["Latihan yang disarankan"],
    "further_reading": ["Bacaan lanjutan"],
    "summary": "Ringkasan singkat materi"
}}

Pastikan output dalam format JSON yang valid dan lengkap.
"""

def create_general_summary_prompt(text: str) -> str:
    """
    Membuat prompt untuk general summarization.
    """
    return f"""
Ringkas teks berikut dengan format yang terstruktur:

Teks: {text}

Format output:
📋 RINGKASAN EKSEKUTIF
[Ringkasan singkat dalam 2-3 kalimat]

🎯 POIN-POIN UTAMA
• [Poin 1]
• [Poin 2]
• [Poin 3]

📝 INFORMASI PENTING
• [Informasi 1]
• [Informasi 2]

✅ KESIMPULAN
• [Kesimpulan 1]
• [Kesimpulan 2]

⚠️ HAL YANG PERLU DIPERHATIKAN
• [Hal 1]
• [Hal 2]

📅 TIMELINE (jika ada)
• [Timeline 1]
• [Timeline 2]

Buat ringkasan yang informatif, terstruktur, dan mudah dibaca.
"""

def create_youtube_summary_prompt(text: str) -> str:
    """
    Membuat prompt untuk YouTube video summarization.
    """
    return f"""
TUGAS: Buat ringkasan video YouTube yang informatif dan terstruktur dari transkripsi berikut.

PETUNJUK:
1. Identifikasi topik utama dan tujuan video
2. Ekstrak poin-poin penting dan informasi kunci
3. Catat tips, tutorial, atau rekomendasi yang diberikan
4. Identifikasi produk, layanan, atau referensi yang disebutkan
5. Ringkas dalam format yang mudah dipahami

TRANSCRIPSI VIDEO YOUTUBE:
{text}

FORMAT OUTPUT (dalam JSON):
{{
    "video_info": {{
        "title": "Judul video berdasarkan konteks",
        "creator": "Nama creator/channel jika disebutkan",
        "category": "Kategori video (tutorial/review/entertainment/dll)",
        "duration": "Perkiraan durasi berdasarkan transkripsi"
    }},
    "executive_summary": "Ringkasan singkat video dalam 2-3 kalimat",
    "main_topics": ["Topik utama yang dibahas"],
    "key_points": [
        {{
            "point": "Poin penting",
            "description": "Penjelasan detail",
            "timestamp": "Perkiraan timestamp jika disebutkan",
            "importance": "Mengapa penting"
        }}
    ],
    "tutorial_steps": [
        {{
            "step": "Langkah tutorial",
            "description": "Penjelasan langkah",
            "tips": "Tips tambahan jika ada"
        }}
    ],
    "products_mentioned": [
        {{
            "product": "Nama produk",
            "description": "Deskripsi produk",
            "opinion": "Opini creator tentang produk",
            "link": "Link jika disebutkan"
        }}
    ],
    "tips_and_tricks": ["Tips dan trik yang dibagikan"],
    "recommendations": ["Rekomendasi dari creator"],
    "call_to_action": "Aksi yang diminta creator (subscribe/like/comment)",
    "related_content": ["Konten terkait yang disebutkan"],
    "credits": ["Credit atau shoutout yang diberikan"]
}}

Pastikan output dalam format JSON yang valid dan lengkap.
"""

def create_content_specific_prompt(text: str, content_type: str = None) -> str:
    """
    Membuat prompt berdasarkan jenis konten yang terdeteksi.
    """
    if not content_type:
        content_type = detect_content_type(text)
    
    prompt_functions = {
        'meeting': create_meeting_summary_prompt,
        'document': create_document_summary_prompt,
        'presentation': create_presentation_summary_prompt,
        'interview': create_interview_summary_prompt,
        'lecture': create_lecture_summary_prompt,
        'youtube': create_youtube_summary_prompt,
        'general': create_general_summary_prompt
    }
    
    prompt_function = prompt_functions.get(content_type, create_general_summary_prompt)
    return prompt_function(text)

def format_content_specific_output(parsed_data: Dict[str, Any], original_text: str, content_type: str) -> str:
    """
    Format output berdasarkan jenis konten.
    """
    if parsed_data.get("format") == "text":
        return parsed_data["content"]
    
    output = []
    
    # Header berdasarkan jenis konten
    content_headers = {
        'meeting': "📋 RINGKASAN MEETING",
        'document': "📄 RINGKASAN DOKUMEN",
        'presentation': "📊 RINGKASAN PRESENTASI",
        'interview': "🎤 RINGKASAN WAWANCARA",
        'lecture': "📚 RINGKASAN MATERI PEMBELAJARAN",
        'youtube': "📺 RINGKASAN VIDEO YOUTUBE",
        'general': "📋 RINGKASAN"
    }
    
    header = content_headers.get(content_type, "📋 RINGKASAN")
    output.append("=" * 60)
    output.append(header)
    output.append("=" * 60)
    output.append("")
    
    # Format berdasarkan jenis konten
    if content_type == 'meeting':
        output.extend(format_meeting_output(parsed_data))
    elif content_type == 'document':
        output.extend(format_document_output(parsed_data))
    elif content_type == 'presentation':
        output.extend(format_presentation_output(parsed_data))
    elif content_type == 'interview':
        output.extend(format_interview_output(parsed_data))
    elif content_type == 'lecture':
        output.extend(format_lecture_output(parsed_data))
    elif content_type == 'youtube':
        output.extend(format_youtube_output(parsed_data))
    else:
        output.extend(format_general_output(parsed_data))
    
    # Footer
    output.append("=" * 60)
    output.append(f"📄 Dibuat pada: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    output.append(f"📊 Total karakter transkripsi: {len(original_text)}")
    output.append(f"🏷️ Jenis konten: {content_type.title()}")
    output.append("=" * 60)
    
    return "\n".join(output)

def format_meeting_output(parsed_data: Dict[str, Any]) -> List[str]:
    """Format output untuk meeting."""
    output = []
    
    # Meeting Info
    meeting_info = parsed_data.get("meeting_info", {})
    if meeting_info:
        output.append("📅 INFORMASI MEETING")
        output.append(f"Judul: {meeting_info.get('title', 'Tidak disebutkan')}")
        output.append(f"Tanggal: {meeting_info.get('date', 'Tidak disebutkan')}")
        output.append(f"Durasi: {meeting_info.get('duration', 'Tidak disebutkan')}")
        if meeting_info.get('participants'):
            output.append(f"Peserta: {', '.join(meeting_info['participants'])}")
        output.append("")
    
    # Executive Summary
    if parsed_data.get("executive_summary"):
        output.append("🎯 RINGKASAN EKSEKUTIF")
        output.append(parsed_data["executive_summary"])
        output.append("")
    
    # Agenda
    if parsed_data.get("agenda"):
        output.append("📋 AGENDA")
        for i, item in enumerate(parsed_data["agenda"], 1):
            output.append(f"{i}. {item}")
        output.append("")
    
    # Key Points
    if parsed_data.get("key_points"):
        output.append("🔑 POIN-POIN UTAMA")
        for i, point in enumerate(parsed_data["key_points"], 1):
            output.append(f"{i}. {point.get('topic', 'Topik')}")
            output.append(f"   Ringkasan: {point.get('summary', 'Tidak ada ringkasan')}")
            if point.get('decisions'):
                output.append(f"   Keputusan: {', '.join(point['decisions'])}")
            if point.get('notes'):
                output.append(f"   Catatan: {point['notes']}")
            output.append("")
    
    # Action Items
    if parsed_data.get("action_items"):
        output.append("✅ ACTION ITEMS")
        for i, item in enumerate(parsed_data["action_items"], 1):
            output.append(f"{i}. {item.get('task', 'Tugas')}")
            output.append(f"   Tanggung Jawab: {item.get('assignee', 'Tidak ditentukan')}")
            if item.get('deadline'):
                output.append(f"   Deadline: {item['deadline']}")
            if item.get('priority'):
                output.append(f"   Prioritas: {item['priority']}")
            output.append("")
    
    # Risk Issues
    if parsed_data.get("risk_issues"):
        output.append("⚠️ MASALAH/RISIKO")
        for i, risk in enumerate(parsed_data["risk_issues"], 1):
            output.append(f"{i}. {risk}")
        output.append("")
    
    # Success Metrics
    if parsed_data.get("success_metrics"):
        output.append("📊 METRIK KEBERHASILAN")
        for i, metric in enumerate(parsed_data["success_metrics"], 1):
            output.append(f"{i}. {metric}")
        output.append("")
    
    # Next Meeting
    next_meeting = parsed_data.get("next_meeting", {})
    if next_meeting.get("scheduled") == "Ya":
        output.append("📅 MEETING BERIKUTNYA")
        output.append(f"Tanggal: {next_meeting.get('date', 'Tidak ditentukan')}")
        if next_meeting.get('agenda'):
            output.append(f"Agenda: {next_meeting['agenda']}")
        output.append("")
    
    return output

def format_document_output(parsed_data: Dict[str, Any]) -> List[str]:
    """Format output untuk document."""
    output = []
    
    # Document Info
    doc_info = parsed_data.get("document_info", {})
    if doc_info:
        output.append("📄 INFORMASI DOKUMEN")
        output.append(f"Judul: {doc_info.get('title', 'Tidak disebutkan')}")
        output.append(f"Jenis: {doc_info.get('type', 'Tidak disebutkan')}")
        output.append(f"Penulis: {doc_info.get('author', 'Tidak disebutkan')}")
        output.append(f"Tanggal: {doc_info.get('date', 'Tidak disebutkan')}")
        output.append("")
    
    # Executive Summary
    if parsed_data.get("executive_summary"):
        output.append("🎯 RINGKASAN EKSEKUTIF")
        output.append(parsed_data["executive_summary"])
        output.append("")
    
    # Objectives
    if parsed_data.get("objectives"):
        output.append("🎯 TUJUAN")
        for i, obj in enumerate(parsed_data["objectives"], 1):
            output.append(f"{i}. {obj}")
        output.append("")
    
    # Methodology
    methodology = parsed_data.get("methodology", {})
    if methodology:
        output.append("🔬 METODOLOGI")
        if methodology.get("approach"):
            output.append(f"Pendekatan: {methodology['approach']}")
        if methodology.get("data_sources"):
            output.append(f"Sumber Data: {', '.join(methodology['data_sources'])}")
        if methodology.get("tools"):
            output.append(f"Tools: {', '.join(methodology['tools'])}")
        output.append("")
    
    # Key Findings
    if parsed_data.get("key_findings"):
        output.append("🔍 TEMUAN UTAMA")
        for i, finding in enumerate(parsed_data["key_findings"], 1):
            output.append(f"{i}. {finding.get('finding', 'Temuan')}")
            output.append(f"   Deskripsi: {finding.get('description', 'Tidak ada deskripsi')}")
            output.append(f"   Signifikansi: {finding.get('significance', 'Tidak disebutkan')}")
            output.append("")
    
    # Conclusions
    if parsed_data.get("conclusions"):
        output.append("✅ KESIMPULAN")
        for i, conclusion in enumerate(parsed_data["conclusions"], 1):
            output.append(f"{i}. {conclusion}")
        output.append("")
    
    # Recommendations
    if parsed_data.get("recommendations"):
        output.append("💡 REKOMENDASI")
        for i, rec in enumerate(parsed_data["recommendations"], 1):
            output.append(f"{i}. {rec.get('recommendation', 'Rekomendasi')}")
            output.append(f"   Prioritas: {rec.get('priority', 'Tidak ditentukan')}")
            if rec.get('implementation'):
                output.append(f"   Implementasi: {rec['implementation']}")
            output.append("")
    
    return output

def format_presentation_output(parsed_data: Dict[str, Any]) -> List[str]:
    """Format output untuk presentation."""
    output = []
    
    # Presentation Info
    pres_info = parsed_data.get("presentation_info", {})
    if pres_info:
        output.append("📊 INFORMASI PRESENTASI")
        output.append(f"Judul: {pres_info.get('title', 'Tidak disebutkan')}")
        output.append(f"Pembicara: {pres_info.get('presenter', 'Tidak disebutkan')}")
        output.append(f"Audience: {pres_info.get('audience', 'Tidak disebutkan')}")
        output.append(f"Durasi: {pres_info.get('duration', 'Tidak disebutkan')}")
        output.append("")
    
    # Overview
    if parsed_data.get("overview"):
        output.append("📋 OVERVIEW")
        output.append(parsed_data["overview"])
        output.append("")
    
    # Objectives
    if parsed_data.get("objectives"):
        output.append("🎯 TUJUAN")
        for i, obj in enumerate(parsed_data["objectives"], 1):
            output.append(f"{i}. {obj}")
        output.append("")
    
    # Key Sections
    if parsed_data.get("key_sections"):
        output.append("📑 BAGIAN UTAMA")
        for i, section in enumerate(parsed_data["key_sections"], 1):
            output.append(f"{i}. {section.get('section', 'Section')}")
            output.append(f"   Konten: {section.get('content', 'Tidak ada konten')}")
            if section.get('key_points'):
                output.append(f"   Poin Kunci: {', '.join(section['key_points'])}")
            if section.get('data'):
                output.append(f"   Data: {', '.join(section['data'])}")
            output.append("")
    
    # Main Arguments
    if parsed_data.get("main_arguments"):
        output.append("💭 ARGUMEN UTAMA")
        for i, arg in enumerate(parsed_data["main_arguments"], 1):
            output.append(f"{i}. {arg}")
        output.append("")
    
    # Conclusions
    if parsed_data.get("conclusions"):
        output.append("✅ KESIMPULAN")
        for i, conclusion in enumerate(parsed_data["conclusions"], 1):
            output.append(f"{i}. {conclusion}")
        output.append("")
    
    # Call to Action
    if parsed_data.get("call_to_action"):
        output.append("🎯 CALL TO ACTION")
        output.append(parsed_data["call_to_action"])
        output.append("")
    
    return output

def format_interview_output(parsed_data: Dict[str, Any]) -> List[str]:
    """Format output untuk interview."""
    output = []
    
    # Interview Info
    int_info = parsed_data.get("interview_info", {})
    if int_info:
        output.append("🎤 INFORMASI WAWANCARA")
        output.append(f"Topik: {int_info.get('topic', 'Tidak disebutkan')}")
        output.append(f"Responden: {int_info.get('interviewee', 'Tidak disebutkan')}")
        output.append(f"Pewawancara: {int_info.get('interviewer', 'Tidak disebutkan')}")
        output.append(f"Tanggal: {int_info.get('date', 'Tidak disebutkan')}")
        output.append("")
    
    # Background
    if parsed_data.get("background"):
        output.append("👤 LATAR BELAKANG")
        output.append(parsed_data["background"])
        output.append("")
    
    # Key Questions
    if parsed_data.get("key_questions"):
        output.append("❓ PERTANYAAN UTAMA")
        for i, qa in enumerate(parsed_data["key_questions"], 1):
            output.append(f"{i}. {qa.get('question', 'Pertanyaan')}")
            output.append(f"   Jawaban: {qa.get('answer', 'Tidak ada jawaban')}")
            if qa.get('insights'):
                output.append(f"   Insight: {', '.join(qa['insights'])}")
            output.append("")
    
    # Main Themes
    if parsed_data.get("main_themes"):
        output.append("🎨 TEMA UTAMA")
        for i, theme in enumerate(parsed_data["main_themes"], 1):
            output.append(f"{i}. {theme}")
        output.append("")
    
    # Experiences
    if parsed_data.get("experiences"):
        output.append("💼 PENGALAMAN")
        for i, exp in enumerate(parsed_data["experiences"], 1):
            output.append(f"{i}. {exp}")
        output.append("")
    
    # Recommendations
    if parsed_data.get("recommendations"):
        output.append("💡 REKOMENDASI")
        for i, rec in enumerate(parsed_data["recommendations"], 1):
            output.append(f"{i}. {rec}")
        output.append("")
    
    # Key Learnings
    if parsed_data.get("key_learnings"):
        output.append("📚 PELAJARAN PENTING")
        for i, learning in enumerate(parsed_data["key_learnings"], 1):
            output.append(f"{i}. {learning}")
        output.append("")
    
    return output

def format_lecture_output(parsed_data: Dict[str, Any]) -> List[str]:
    """Format output untuk lecture."""
    output = []
    
    # Lecture Info
    lec_info = parsed_data.get("lecture_info", {})
    if lec_info:
        output.append("📚 INFORMASI MATERI")
        output.append(f"Judul: {lec_info.get('title', 'Tidak disebutkan')}")
        output.append(f"Pengajar: {lec_info.get('instructor', 'Tidak disebutkan')}")
        output.append(f"Mata Pelajaran: {lec_info.get('subject', 'Tidak disebutkan')}")
        output.append(f"Level: {lec_info.get('level', 'Tidak disebutkan')}")
        output.append("")
    
    # Learning Objectives
    if parsed_data.get("learning_objectives"):
        output.append("🎯 TUJUAN PEMBELAJARAN")
        for i, obj in enumerate(parsed_data["learning_objectives"], 1):
            output.append(f"{i}. {obj}")
        output.append("")
    
    # Main Concepts
    if parsed_data.get("main_concepts"):
        output.append("🧠 KONSEP UTAMA")
        for i, concept in enumerate(parsed_data["main_concepts"], 1):
            output.append(f"{i}. {concept.get('concept', 'Konsep')}")
            output.append(f"   Penjelasan: {concept.get('explanation', 'Tidak ada penjelasan')}")
            if concept.get('examples'):
                output.append(f"   Contoh: {', '.join(concept['examples'])}")
            output.append(f"   Pentingnya: {concept.get('importance', 'Tidak disebutkan')}")
            output.append("")
    
    # Key Theories
    if parsed_data.get("key_theories"):
        output.append("📖 TEORI PENTING")
        for i, theory in enumerate(parsed_data["key_theories"], 1):
            output.append(f"{i}. {theory}")
        output.append("")
    
    # Important Points
    if parsed_data.get("important_points"):
        output.append("⭐ POIN PENTING")
        for i, point in enumerate(parsed_data["important_points"], 1):
            output.append(f"{i}. {point}")
        output.append("")
    
    # Tips and Tricks
    if parsed_data.get("tips_and_tricks"):
        output.append("💡 TIPS DAN TRIK")
        for i, tip in enumerate(parsed_data["tips_and_tricks"], 1):
            output.append(f"{i}. {tip}")
        output.append("")
    
    # Summary
    if parsed_data.get("summary"):
        output.append("📋 RINGKASAN")
        output.append(parsed_data["summary"])
        output.append("")
    
    return output

def format_general_output(parsed_data: Dict[str, Any]) -> List[str]:
    """Format output untuk general content."""
    output = []
    
    # Executive Summary
    if parsed_data.get("executive_summary"):
        output.append("🎯 RINGKASAN EKSEKUTIF")
        output.append(parsed_data["executive_summary"])
        output.append("")
    
    # Key Points
    if parsed_data.get("key_points"):
        output.append("🔑 POIN-POIN UTAMA")
        for i, point in enumerate(parsed_data["key_points"], 1):
            output.append(f"{i}. {point}")
        output.append("")
    
    # Important Information
    if parsed_data.get("important_info"):
        output.append("📝 INFORMASI PENTING")
        for i, info in enumerate(parsed_data["important_info"], 1):
            output.append(f"{i}. {info}")
        output.append("")
    
    # Conclusions
    if parsed_data.get("conclusions"):
        output.append("✅ KESIMPULAN")
        for i, conclusion in enumerate(parsed_data["conclusions"], 1):
            output.append(f"{i}. {conclusion}")
        output.append("")
    
    return output

def format_youtube_output(parsed_data: Dict[str, Any]) -> List[str]:
    """Format output untuk YouTube content."""
    output = []
    
    # Video Info
    video_info = parsed_data.get("video_info", {})
    if video_info:
        output.append("📺 INFORMASI VIDEO")
        output.append(f"Judul: {video_info.get('title', 'Tidak disebutkan')}")
        output.append(f"Creator: {video_info.get('creator', 'Tidak disebutkan')}")
        output.append(f"Kategori: {video_info.get('category', 'Tidak disebutkan')}")
        output.append(f"Durasi: {video_info.get('duration', 'Tidak disebutkan')}")
        output.append("")
    
    # Executive Summary
    if parsed_data.get("executive_summary"):
        output.append("🎯 RINGKASAN VIDEO")
        output.append(parsed_data["executive_summary"])
        output.append("")
    
    # Main Topics
    if parsed_data.get("main_topics"):
        output.append("📋 TOPIK UTAMA")
        for i, topic in enumerate(parsed_data["main_topics"], 1):
            output.append(f"{i}. {topic}")
        output.append("")
    
    # Key Points
    if parsed_data.get("key_points"):
        output.append("🔑 POIN-POIN PENTING")
        for i, point in enumerate(parsed_data["key_points"], 1):
            output.append(f"{i}. {point.get('point', 'Poin')}")
            output.append(f"   Deskripsi: {point.get('description', 'Tidak ada deskripsi')}")
            if point.get('timestamp'):
                output.append(f"   Timestamp: {point['timestamp']}")
            output.append(f"   Pentingnya: {point.get('importance', 'Tidak disebutkan')}")
            output.append("")
    
    # Tutorial Steps
    if parsed_data.get("tutorial_steps"):
        output.append("📝 LANGKAH TUTORIAL")
        for i, step in enumerate(parsed_data["tutorial_steps"], 1):
            output.append(f"{i}. {step.get('step', 'Langkah')}")
            output.append(f"   Deskripsi: {step.get('description', 'Tidak ada deskripsi')}")
            if step.get('tips'):
                output.append(f"   Tips: {step['tips']}")
            output.append("")
    
    # Products Mentioned
    if parsed_data.get("products_mentioned"):
        output.append("🛍️ PRODUK YANG DISEBUTKAN")
        for i, product in enumerate(parsed_data["products_mentioned"], 1):
            output.append(f"{i}. {product.get('product', 'Produk')}")
            output.append(f"   Deskripsi: {product.get('description', 'Tidak ada deskripsi')}")
            if product.get('opinion'):
                output.append(f"   Opini: {product['opinion']}")
            if product.get('link'):
                output.append(f"   Link: {product['link']}")
            output.append("")
    
    # Tips and Tricks
    if parsed_data.get("tips_and_tricks"):
        output.append("💡 TIPS DAN TRIK")
        for i, tip in enumerate(parsed_data["tips_and_tricks"], 1):
            output.append(f"{i}. {tip}")
        output.append("")
    
    # Recommendations
    if parsed_data.get("recommendations"):
        output.append("⭐ REKOMENDASI")
        for i, rec in enumerate(parsed_data["recommendations"], 1):
            output.append(f"{i}. {rec}")
        output.append("")
    
    # Call to Action
    if parsed_data.get("call_to_action"):
        output.append("🎯 CALL TO ACTION")
        output.append(parsed_data["call_to_action"])
        output.append("")
    
    # Related Content
    if parsed_data.get("related_content"):
        output.append("🔗 KONTEN TERKAIT")
        for i, content in enumerate(parsed_data["related_content"], 1):
            output.append(f"{i}. {content}")
        output.append("")
    
    # Credits
    if parsed_data.get("credits"):
        output.append("🙏 CREDIT & SHOUTOUT")
        for i, credit in enumerate(parsed_data["credits"], 1):
            output.append(f"{i}. {credit}")
        output.append("")
    
    return output

def parse_gemini_response(summary_text: str):
    """
    Parse hasil ringkasan Gemini. Jika JSON, kembalikan dict. Jika gagal, fallback ke format text.
    """
    try:
        return json.loads(summary_text)
    except Exception:
        # Fallback: kembalikan format text sederhana
        return {"format": "text", "content": summary_text}

def summarize_with_gemini(text: str, system_prompt: str = None, content_type: str = None):
    """
    Kirim permintaan ringkasan ke Google Gemini 2.0 Flash API dengan output yang terstruktur.
    Return dict jika Gemini mengembalikan JSON, string jika tidak bisa di-parse.
    """
    if not Config.GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY tidak tersedia di environment variables")

    url = f"{Config.GEMINI_API_URL}?key={Config.GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    max_retries = 3
    backoff = 2
    if not content_type:
        content_type = detect_content_type(text)
        logging.info(f"🔍 Content type detected: {content_type}")
    if system_prompt:
        prompt = system_prompt
    else:
        prompt = create_content_specific_prompt(text, content_type)
    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": prompt}]}
        ]
    }
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            summary_text = data["candidates"][0]["content"]["parts"][0]["text"]
            parsed_data = parse_gemini_response(summary_text)
            # Jika hasil parse adalah dict dan bukan fallback format text, return dict
            if isinstance(parsed_data, dict) and parsed_data.get("format") != "text":
                return parsed_data
            # Jika fallback, return string plain
            return summary_text
        except json.JSONDecodeError as e:
            logging.warning(f"[Gemini] JSON parsing failed, using simple format: {e}")
            fallback_prompt = create_simple_summary_prompt(text)
            payload["contents"][0]["parts"][0]["text"] = fallback_prompt
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                data = response.json()
                summary_text = data["candidates"][0]["content"]["parts"][0]["text"]
                return summary_text
            except Exception as e2:
                logging.warning(f"[Gemini] Fallback request failed: {e2}")
                if attempt < max_retries - 1:
                    time.sleep(backoff ** attempt)
                else:
                    logging.error(f"[Gemini] Error: {e2}")
                    raise Exception(f"Gemini API error: {e2}")
        except (requests.exceptions.RequestException, Exception) as e:
            logging.warning(f"[Gemini] API request failed (attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(backoff ** attempt)
            else:
                logging.error(f"[Gemini] Error: {e}")
                raise Exception(f"Gemini API error: {e}")

def create_summary_metadata(text: str, summary: str, content_type: str = None) -> Dict[str, Any]:
    """
    Membuat metadata untuk summary dengan informasi content type.
    """
    if not content_type:
        content_type = detect_content_type(text)
    
    return {
        "generated_at": datetime.now().isoformat(),
        "original_length": len(text),
        "summary_length": len(summary),
        "compression_ratio": round(len(summary) / len(text) * 100, 2) if text else 0,
        "word_count_original": len(text.split()),
        "word_count_summary": len(summary.split()),
        "processing_engine": "Gemini 2.0 Flash",
        "format_version": "2.0",
        "content_type": content_type,
        "content_type_detected": True
    } 