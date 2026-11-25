"""Genera capturas de la interfaz en evidencias/ (requiere el servidor en :8000 y playwright).
Uso: python pruebas/capturas_ui.py"""
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent.parent / "evidencias"
URL = "http://localhost:8000/"


def entrar(pg, email):
    pg.goto(URL); pg.evaluate("sessionStorage.clear()"); pg.reload()
    pg.fill("#email", email); pg.fill("#password", "demo123"); pg.click("#btnAcceso")
    pg.wait_for_selector("#app:not(.oculto)")


with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 820})

    # Solicitante: crea una solicitud (CA-01)
    entrar(pg, "solicitante@demo.com")
    pg.click("#btnNueva")
    pg.fill("#n_titulo", "Paz y salvo académico")
    pg.fill("#n_desc", "Necesito el paz y salvo para tramitar mi grado.")
    pg.select_option("#n_cat", "Trámite"); pg.select_option("#n_prio", "alta")
    pg.screenshot(path=str(OUT / "ui_01_solicitante_nueva.png"))
    pg.click("form.nueva button[type=submit]"); pg.wait_for_selector(".detalle")
    pg.screenshot(path=str(OUT / "ui_02_solicitante_registrada.png"))

    # Personal: evalúa, gestiona y finaliza (CA-02, CA-03, CA-04)
    entrar(pg, "personal@demo.com")
    pg.click("ul.lista li:first-child"); pg.wait_for_selector("form.gestion")
    pg.select_option("#g_estado", "EN_REVISION"); pg.fill("#g_com", "Tomo el caso para revisión")
    pg.click("form.gestion button[type=submit]"); pg.wait_for_selector("text=Tomo el caso para revisión")
    pg.select_option("#g_estado", "EN_GESTION"); pg.fill("#g_com", "Gestiono el documento con secretaría")
    pg.click("form.gestion button[type=submit]"); pg.wait_for_selector("text=Gestiono el documento")
    pg.screenshot(path=str(OUT / "ui_03_personal_gestion.png"))
    pg.select_option("#g_estado", "FINALIZADA"); pg.fill("#g_com", "Documento emitido")
    pg.fill("#g_resp", "Tu paz y salvo fue emitido y enviado a tu correo.")
    pg.click("form.gestion button[type=submit]"); pg.wait_for_selector(".respuesta")
    pg.screenshot(path=str(OUT / "ui_04_personal_finalizada.png"))

    # Solicitante: ve la respuesta (CA-05)
    entrar(pg, "solicitante@demo.com")
    pg.click("ul.lista li:first-child"); pg.wait_for_selector(".respuesta")
    pg.screenshot(path=str(OUT / "ui_05_solicitante_respuesta.png"))

    # Coordinación: resumen (CA-06)
    entrar(pg, "coordinacion@demo.com"); pg.wait_for_selector("#resumenCajas .caja")
    pg.screenshot(path=str(OUT / "ui_06_coordinacion_resumen.png"))
    b.close()
print("Capturas guardadas en", OUT)
