from flask import Blueprint, render_template_string

public = Blueprint("public", __name__)

TEMPLATE = """<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{{ title }} · IntelliHire</title><style>body{margin:0;background:#071426;color:#eef6ff;font-family:system-ui,sans-serif}main{max-width:1000px;margin:auto;padding:48px 22px}.nav{max-width:1000px;margin:auto;padding:22px;display:flex;justify-content:space-between}.nav a{color:#bfeaff;text-decoration:none;margin-left:16px}.hero{padding:42px 0}.eyebrow{color:#68e7ff;font-size:12px;letter-spacing:.16em;font-weight:800}h1{font-size:clamp(40px,7vw,68px);line-height:1;margin:14px 0}p{color:#b9c9db;line-height:1.7;font-size:18px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}.card{padding:22px;background:#0d1c33;border:1px solid #24405f;border-radius:18px}.cta{display:inline-block;padding:12px 16px;background:#35c8ff;color:#04111e!important;border-radius:10px;font-weight:800;text-decoration:none}@media(max-width:700px){.nav a:not(.cta){display:none}}</style></head><body><nav class='nav'><a href='/'><strong>✦ INTELLIHIRE</strong></a><div><a href='/about'>About</a><a href='/how-it-works'>How it works</a><a href='/features'>Features</a><a href='/pricing'>Pricing</a><a href='/contact'>Contact</a><a class='cta' href='/auth/google'>Start</a></div></nav><main>{{ body|safe }}</main></body></html>"""

def page(title, body):
    return render_template_string(TEMPLATE, title=title, body=body)

@public.get('/about')
def about():
    return page('About', "<section class='hero'><div class='eyebrow'>ABOUT INTELLIHIRE</div><h1>Train smart. Perform better. Get placed.</h1><p>IntelliHire brings resume intelligence, adaptive assessment, technical interview practice, HR coaching, behavioural insight, and readiness into one structured candidate journey.</p></section>")

@public.get('/how-it-works')
def how_it_works():
    steps=['01 Resume Screening','02 Adaptive Assessment','03 Technical Interview','04 HR & Behaviour','05 Candidate Readiness']
    cards=''.join(f"<article class='card'><h2>{s}</h2><p>Practice this stage, review performance signals, and continue to the next step.</p></article>" for s in steps)
    return page('How it works', f"<section class='hero'><div class='eyebrow'>THE JOURNEY</div><h1>One flow from resume to readiness.</h1><p>Work through the major stages of a modern recruitment process with measurable preparation feedback.</p></section><section class='grid'>{cards}</section>")

@public.get('/features')
def features():
    items=['AI Resume Intelligence','Adaptive Assessment','Technical Interview','HR Interview Coaching','Behavioural Analysis','Readiness Intelligence','Progress Tracking','AI Provider Resilience']
    cards=''.join(f"<article class='card'><h2>{x}</h2><p>Production-oriented candidate preparation with clear feedback and recovery paths.</p></article>" for x in items)
    return page('Features', f"<section class='hero'><div class='eyebrow'>CAPABILITIES</div><h1>Every major preparation stage in one place.</h1><p>Use structured practice to understand strengths, weaknesses, and what to work on next.</p></section><section class='grid'>{cards}</section>")

@public.get('/pricing')
def pricing():
    return page('Pricing', "<section class='hero'><div class='eyebrow'>PRICING</div><h1>Practice first.</h1><p>The current candidate experience focuses on product validation and placement preparation. No payment details are collected on this page.</p><a class='cta' href='/auth/google'>Start practicing</a></section>")

@public.get('/contact')
def contact():
    return page('Contact', "<section class='hero'><div class='eyebrow'>CONTACT</div><h1>Bring IntelliHire to your placement workflow.</h1><p>For product feedback, training-program enquiries, or partnerships, continue into the authenticated product flow.</p><a class='cta' href='/auth/google'>Continue to IntelliHire</a></section>")
