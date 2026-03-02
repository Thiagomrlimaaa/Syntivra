"""
Script para extrair texto dos PDFs e salvar em arquivos de texto
para análise antes de inserir no banco.
"""
import sys
sys.path.insert(0, '.')

import pdfplumber
import os

pdfs = [
    r"C:\Users\AVELL\Documents\Syntivra\PALMAS_GLOSSARIO.pdf",
    r"C:\Users\AVELL\Documents\Syntivra\Manual___Modulo_Processos.pdf",
    r"C:\Users\AVELL\Documents\Syntivra\Manual___Modulo_Documentos.pdf",
]

for pdf_path in pdfs:
    name = os.path.basename(pdf_path).replace('.pdf', '')
    print(f"\n=== Processando: {name} ===")
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"  Total de páginas: {total_pages}")
            
            all_text = []
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text and text.strip():
                    all_text.append(f"[Página {i+1}]\n{text.strip()}")
            
            full_text = "\n\n".join(all_text)
            print(f"  Caracteres extraídos: {len(full_text)}")
            print(f"  Preview (300 chars):\n    {full_text[:300].encode('utf-8', errors='replace').decode('utf-8')}")
            
            out_file = f"pdf_extract_{name}.txt"
            with open(out_file, 'w', encoding='utf-8', errors='replace') as f:
                f.write(full_text)
            print(f"  Salvo em: {out_file}")
            
    except Exception as e:
        print(f"  ERRO: {e}")

print("\n\nExtração concluída.")
