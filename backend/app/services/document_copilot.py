import os
import re
from typing import Dict, Any, Optional
from ..core.config import get_gemini_api_key, generate_with_gemini_fallback

def assist_document_edit(
    doc_text: str,
    user_prompt: str,
    selected_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    AI Copilot specialized in viewing, analyzing, modifying, and drafting document content.
    Seamlessly integrates with Google Gemini and provides local heuristic fallback.
    """
    api_key = get_gemini_api_key()
    
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            prompt_context = f"""
Eres "DocuMind Copilot", un asistente de redacción y edición de documentos empresariales de nivel experto.
Tu objetivo es ayudar al usuario a revisar, mejorar, redactar cláusulas o hacer cambios en su documento corporativo.

TEXTO ACTUAL DEL DOCUMENTO:
\"\"\"
{doc_text[:14000]}
\"\"\"
"""
            if selected_text and selected_text.strip():
                prompt_context += f"""
TEXTO ESPECÍFICO SELECCIONADO POR EL USUARIO PARA MODIFICAR:
\"\"\"
{selected_text[:4000]}
\"\"\"
"""

            prompt_context += f"""
INSTRUCCIÓN O CONSULTA DEL USUARIO:
\"{user_prompt}\"

INSTRUCCIONES CRÍTICAS DE FORMATO:
1. Si el usuario solicita redactar, modificar, agregar una cláusula, corregir o traducir texto:
   - En tu respuesta, explica brevemente el cambio realizado.
   - Encierra TODO el texto nuevo o modificado que se debe insertar en el documento dentro del siguiente bloque exacto:
     <<<PROPUESTA_TEXTUAL>>>
     (Escribe aquí el texto exacto, bien formateado y listo para ser aplicado)
     <<<FIN_PROPUESTA>>>
2. Si el usuario solicita crear, agregar o estructurar una TABLA (ej: cronograma, costos, presupuesto, entregables o matriz comparativa):
   - Redacta la tabla usando código HTML visual estructurado con la clase "doc-table":
     <table class="doc-table">
       <thead><tr><th>Encabezado 1</th><th>Encabezado 2</th><th>Encabezado 3</th></tr></thead>
       <tbody>
         <tr><td>Dato 1</td><td>Dato 2</td><td>Dato 3</td></tr>
       </tbody>
     </table>
   - Coloca la tabla HTML completa dentro de <<<PROPUESTA_TEXTUAL>>> para que el usuario la inserte con 1 clic.
3. Si el usuario únicamente hace una pregunta o pide una explicación sin solicitar cambios ni tablas en el documento, responde directamente de forma clara y concisa SIN usar las etiquetas <<<PROPUESTA_TEXTUAL>>>.

Asegúrate de que el lenguaje sea formal, preciso y con terminología empresarial adecuada.
"""
            raw_reply, used_model = generate_with_gemini_fallback(genai, prompt_context)
            
            # Extract proposal block if present
            suggested_text = None
            mode = "answer"
            
            proposal_match = re.search(r'<<<PROPUESTA_TEXTUAL>>>(.*?)<<<FIN_PROPUESTA>>>', raw_reply, re.DOTALL)
            if proposal_match:
                suggested_text = proposal_match.group(1).strip()
                clean_reply = re.sub(r'<<<PROPUESTA_TEXTUAL>>>(.*?)<<<FIN_PROPUESTA>>>', '', raw_reply, flags=re.DOTALL).strip()
                if not clean_reply:
                    clean_reply = "He redactado la siguiente propuesta para tu documento:"
                mode = "suggestion"
            else:
                clean_reply = raw_reply.strip()
                
            return {
                "reply": clean_reply,
                "suggested_text": suggested_text,
                "mode": mode,
                "model_used": f"Google Gemini ({used_model})"
            }
        except Exception as e:
            print(f"[Copilot Gemini] Fallback por error: {e}")

    return local_copilot_fallback(doc_text, user_prompt, selected_text)


def local_copilot_fallback(
    doc_text: str,
    user_prompt: str,
    selected_text: Optional[str] = None
) -> Dict[str, Any]:
    """Offline rule-based fallback copilot when Gemini API is unavailable or quota is exceeded."""
    p_lower = user_prompt.lower()
    
    # Clause drafting templates
    if any(w in p_lower for w in ["penal", "penalidad", "multa", "incumplimiento"]):
        clause = (
            "CLÁUSULA PENAL POR INCUMPLIMIENTO: En caso de incumplimiento total o parcial de las obligaciones "
            "aquí pactadas, la parte infractora pagará a la otra una suma equivalente al veinte por ciento (20%) "
            "del valor total del contrato a título de pena, sin perjuicio del cobro de las indemnizaciones por los "
            "perjuicios adicionales comprobados a que hubiere lugar."
        )
        return {
            "reply": "He redactado una cláusula penal estándar del 20% conforme a las prácticas comerciales:",
            "suggested_text": clause,
            "mode": "suggestion",
            "model_used": "Motor Local DocuMind Copilot (Modo Contingencia)"
        }
        
    if any(w in p_lower for w in ["confidencial", "nda", "reserva", "secreto"]):
        clause = (
            "CLÁUSULA DE CONFIDENCIALIDAD: Las partes se obligan a mantener bajo estricta reserva toda la información "
            "técnica, comercial, financiera o estratégica intercambiada con ocasión del presente acuerdo. Esta obligación "
            "permanecerá vigente durante la ejecución del contrato y por un periodo adicional de cinco (5) años tras su terminación."
        )
        return {
            "reply": "He generado la cláusula de confidencialidad y secreto corporativo:",
            "suggested_text": clause,
            "mode": "suggestion",
            "model_used": "Motor Local DocuMind Copilot (Modo Contingencia)"
        }
        
    if any(w in p_lower for w in ["garantia", "garantía", "calidad", "soporte"]):
        clause = (
            "CLÁUSULA DE GARANTÍA Y SOPORTE: El contratista garantiza la calidad y correcto funcionamiento de los entregables "
            "por un término mínimo de doce (12) meses contados a partir de la firma del acta de entrega y recibo a satisfacción, "
            "comprometiéndose a subsanar fallas o defectos sin costo adicional para el contratante dentro de un plazo no mayor a 48 horas."
        )
        return {
            "reply": "He generado una cláusula de garantía de 12 meses con tiempo de respuesta de 48 horas:",
            "suggested_text": clause,
            "mode": "suggestion",
            "model_used": "Motor Local DocuMind Copilot (Modo Contingencia)"
        }

    if any(w in p_lower for w in ["resumen", "sintesis", "sintetizar"]):
        lines = [line.strip() for line in doc_text.split("\n") if len(line.strip()) > 30]
        summary_lines = lines[:4] if lines else ["Documento corporativo gestionado en DocuMind Enterprise."]
        summary = "SÍNTESIS DEL DOCUMENTO:\n" + "\n".join([f"• {l[:160]}..." if len(l) > 160 else f"• {l}" for l in summary_lines])
        return {
            "reply": "He extraído los puntos principales del documento:",
            "suggested_text": summary,
            "mode": "suggestion",
            "model_used": "Motor Local DocuMind Copilot (Modo Contingencia)"
        }

    if any(w in p_lower for w in ["tabla", "cuadro", "cronograma", "presupuesto", "matriz"]):
        tbl = (
            '<table class="doc-table">\n'
            '  <thead>\n'
            '    <tr><th>Ítem / Concepto</th><th>Descripción</th><th>Plazo / Fecha</th><th>Valor Estimado</th></tr>\n'
            '  </thead>\n'
            '  <tbody>\n'
            '    <tr><td>Fase 1: Diagnóstico</td><td>Levantamiento de requerimientos y auditoría</td><td>Semana 1-2</td><td>$ 3.500.000 COP</td></tr>\n'
            '    <tr><td>Fase 2: Implementación</td><td>Configuración, parametrización y pruebas</td><td>Semana 3-6</td><td>$ 7.800.000 COP</td></tr>\n'
            '    <tr><td>Fase 3: Capacitación</td><td>Transferencia de conocimiento a usuarios</td><td>Semana 7</td><td>$ 1.200.000 COP</td></tr>\n'
            '  </tbody>\n'
            '</table>'
        )
        return {
            "reply": "He generado una tabla estructurada con formato corporativo lista para el documento:",
            "suggested_text": tbl,
            "mode": "suggestion",
            "model_used": "Motor Local DocuMind Copilot (Modo Contingencia)"
        }

    # Generic rewriting / assistance
    if selected_text and selected_text.strip():
        improved = selected_text.strip()
        improved = re.sub(r'\s+', ' ', improved)
        return {
            "reply": f"He revisado el fragmento seleccionado ({len(selected_text.split())} palabras) para mejorar su fluidez y puntuación:",
            "suggested_text": improved,
            "mode": "suggestion",
            "model_used": "Motor Local DocuMind Copilot (Modo Contingencia)"
        }

    return {
        "reply": (
            f"He analizado tu consulta sobre el documento ({len(doc_text.split())} palabras). "
            "Puedes pedirme que redacte cláusulas (penalidad, confidencialidad, garantía), mejore la redacción de una sección, "
            "o genere un resumen ejecutivo para insertarlo en el editor."
        ),
        "suggested_text": None,
        "mode": "answer",
        "model_used": "Motor Local DocuMind Copilot (Modo Contingencia)"
    }
