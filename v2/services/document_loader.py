"""
Document Loader - Direct Access to Manual Content
No HTTP calls - direct database and file access
Use this module to fetch document content directly from references

Location: microservices/document_loader.py
"""

import sys
import os
from typing import List, Dict, Any, Optional
import fitz  # PyMuPDF
import logging

# Add v2 to path for database access
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v2'))
from manuals_db import ManualsDB

logger = logging.getLogger(__name__)


class DocumentLoader:
    """
    Direct access to manual content from references
    No HTTP calls - pure Python module
    
    Usage:
        loader = DocumentLoader(db_path='./v2/manuals.db', pdf_path='./v2/manuals/')
        
        # Get content from section references
        content = loader.get_sections_content([
            {"section_id": "RAG_1_45"},
            {"section_id": "RAG_1_50"}
        ])
        
        # Get content from page references
        content = loader.get_pages_content(
            manual_id=1,
            page_numbers=[45, 46, 47]
        )
    """
    
    def __init__(
        self, 
        db_path: str = './v2/manuals.db',
        pdf_base_path: str = './v2/manuals/'
    ):
        """
        Initialize document loader
        
        Args:
            db_path: Path to manuals.db
            pdf_base_path: Path to PDF files folder
        """
        self.db = ManualsDB(db_path)
        self.pdf_base_path = pdf_base_path
        logger.info(f"DocumentLoader initialized: db={db_path}, pdfs={pdf_base_path}")
    
    def get_sections_content(
        self, 
        section_references: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Get full content for section references
        
        Args:
            section_references: List of section refs like:
                [
                    {"section_id": "RAG_1_45"},
                    {"section_id": "RAG_1_50", "include_images": True}
                ]
        
        Returns:
            List of sections with full content:
                [
                    {
                        "section_id": "RAG_1_45",
                        "section_name": "Engine Oil Check",
                        "page_numbers": [45, 46, 47],
                        "full_text": "Complete text from all pages...",
                        "images": ["IMG_1_45", "IMG_1_46"] (if requested),
                        "metadata": {...}
                    }
                ]
        """
        results = []
        
        for ref in section_references:
            section_id = ref.get('section_id')
            if not section_id:
                logger.warning(f"Section reference missing section_id: {ref}")
                continue
            
            # Parse section_id: "RAG_manual_id_first_page"
            parts = section_id.split('_')
            if len(parts) != 3 or parts[0] != 'RAG':
                logger.warning(f"Invalid section_id format: {section_id}")
                continue
            
            try:
                manual_id = int(parts[1])
                first_page = int(parts[2])
            except ValueError:
                logger.warning(f"Invalid section_id: {section_id}")
                continue
            
            # Get section info from database
            self.db.cursor.execute("""
                SELECT section_name, first_page, length, h_level
                FROM Sections
                WHERE manual_id = ? AND first_page = ?
            """, (manual_id, first_page))
            
            row = self.db.cursor.fetchone()
            if not row:
                logger.warning(f"Section not found in DB: {section_id}")
                continue
            
            section_name, first_page, length, h_level = row
            page_numbers = list(range(first_page, first_page + length))
            
            # Extract full text
            full_text = self._extract_text_from_pages(manual_id, first_page, length)
            
            # Optionally include images
            images = []
            if ref.get('include_images', False):
                images = self._get_image_ids(manual_id, first_page, length)
            
            results.append({
                "section_id": section_id,
                "section_name": section_name,
                "page_numbers": page_numbers,
                "full_text": full_text,
                "images": images,
                "metadata": {
                    "manual_id": manual_id,
                    "first_page": first_page,
                    "length": length,
                    "h_level": h_level
                }
            })
        
        logger.info(f"Loaded content for {len(results)} sections")
        return results
    
    def get_pages_content(
        self,
        manual_id: int,
        page_numbers: List[int]
    ) -> Dict[str, Any]:
        """
        Get content from specific pages
        
        Args:
            manual_id: Manual ID
            page_numbers: List of page numbers (0-indexed)
        
        Returns:
            {
                "manual_id": 1,
                "pages": [
                    {
                        "page_number": 45,
                        "text": "Page 45 content..."
                    },
                    {
                        "page_number": 46,
                        "text": "Page 46 content..."
                    }
                ],
                "combined_text": "All pages combined..."
            }
        """
        pdf_path = os.path.join(self.pdf_base_path, f'{manual_id}.pdf')
        
        if not os.path.exists(pdf_path):
            logger.error(f"PDF not found: {pdf_path}")
            return {
                "manual_id": manual_id,
                "pages": [],
                "combined_text": f"[PDF file not found for manual {manual_id}]",
                "error": "PDF not found"
            }
        
        try:
            doc = fitz.open(pdf_path)
            pages_content = []
            all_text = []
            
            for page_num in sorted(page_numbers):
                if page_num >= len(doc):
                    logger.warning(f"Page {page_num} out of range for manual {manual_id}")
                    continue
                
                page = doc[page_num]
                text = page.get_text()
                
                pages_content.append({
                    "page_number": page_num,
                    "text": text
                })
                all_text.append(f"--- Page {page_num + 1} ---\n{text}")
            
            doc.close()
            
            return {
                "manual_id": manual_id,
                "pages": pages_content,
                "combined_text": "\n\n".join(all_text)
            }
        
        except Exception as e:
            logger.error(f"Error extracting pages from {pdf_path}: {e}")
            return {
                "manual_id": manual_id,
                "pages": [],
                "combined_text": f"[Error extracting text: {e}]",
                "error": str(e)
            }
    
    def get_page_content(
        self,
        manual_id: int,
        page_number: int
    ) -> str:
        """
        Get content from a single page
        
        Args:
            manual_id: Manual ID
            page_number: Page number (0-indexed)
        
        Returns:
            Text content of the page
        """
        result = self.get_pages_content(manual_id, [page_number])
        
        if result.get('error'):
            return f"[Error: {result['error']}]"
        
        if not result['pages']:
            return f"[Page {page_number} not found]"
        
        return result['pages'][0]['text']
    
    def get_section_by_name(
        self,
        manual_id: int,
        section_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get section content by searching for section name
        
        Args:
            manual_id: Manual ID
            section_name: Section name to search for (partial match)
        
        Returns:
            Section with full content, or None if not found
        """
        self.db.cursor.execute("""
            SELECT section_name, first_page, length, h_level
            FROM Sections
            WHERE manual_id = ? AND section_name LIKE ?
            LIMIT 1
        """, (manual_id, f"%{section_name}%"))
        
        row = self.db.cursor.fetchone()
        if not row:
            logger.warning(f"Section '{section_name}' not found in manual {manual_id}")
            return None
        
        section_name, first_page, length, h_level = row
        page_numbers = list(range(first_page, first_page + length))
        
        full_text = self._extract_text_from_pages(manual_id, first_page, length)
        images = self._get_image_ids(manual_id, first_page, length)
        
        return {
            "section_id": f"RAG_{manual_id}_{first_page}",
            "section_name": section_name,
            "page_numbers": page_numbers,
            "full_text": full_text,
            "images": images,
            "metadata": {
                "manual_id": manual_id,
                "first_page": first_page,
                "length": length,
                "h_level": h_level
            }
        }
    
    def _extract_text_from_pages(
        self,
        manual_id: int,
        first_page: int,
        length: int
    ) -> str:
        """Extract text from a range of pages"""
        pdf_path = os.path.join(self.pdf_base_path, f'{manual_id}.pdf')
        
        if not os.path.exists(pdf_path):
            logger.error(f"PDF not found: {pdf_path}")
            return f"[PDF file not found for manual {manual_id}]"
        
        try:
            doc = fitz.open(pdf_path)
            text_parts = []
            
            for page_num in range(first_page, min(first_page + length, len(doc))):
                page = doc[page_num]
                text = page.get_text()
                text_parts.append(f"--- Page {page_num + 1} ---\n{text}")
            
            doc.close()
            return "\n\n".join(text_parts)
        
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            return f"[Error extracting text: {e}]"
    
    def _get_image_ids(
        self,
        manual_id: int,
        first_page: int,
        length: int
    ) -> List[str]:
        """Get image IDs for a page range"""
        try:
            self.db.cursor.execute("""
                SELECT page FROM Images 
                WHERE manual_id = ? 
                  AND page >= ? 
                  AND page <= ?
            """, (manual_id, first_page, first_page + length - 1))
            
            image_pages = [row[0] for row in self.db.cursor.fetchall()]
            return [f"IMG_{manual_id}_{page}" for page in image_pages]
        
        except Exception as e:
            logger.error(f"Error getting images: {e}")
            return []
    
    def get_manual_info(self, manual_id: int) -> Optional[Dict[str, Any]]:
        """
        Get manual metadata
        
        Args:
            manual_id: Manual ID
        
        Returns:
            Manual info or None if not found
        """
        self.db.cursor.execute("""
            SELECT manual_id, year, make, model, uplifted, active
            FROM Manuals
            WHERE manual_id = ?
        """, (manual_id,))
        
        row = self.db.cursor.fetchone()
        if not row:
            return None
        
        return {
            "manual_id": row[0],
            "year": row[1],
            "make": row[2],
            "model": row[3],
            "uplifted": bool(row[4]),
            "active": bool(row[5])
        }
    
    def list_sections(self, manual_id: int) -> List[Dict[str, Any]]:
        """
        List all sections in a manual
        
        Args:
            manual_id: Manual ID
        
        Returns:
            List of section metadata (without full text)
        """
        self.db.cursor.execute("""
            SELECT section_name, first_page, length, h_level
            FROM Sections
            WHERE manual_id = ?
            ORDER BY first_page
        """, (manual_id,))
        
        sections = []
        for row in self.db.cursor.fetchall():
            sections.append({
                "section_id": f"RAG_{manual_id}_{row[1]}",
                "section_name": row[0],
                "first_page": row[1],
                "length": row[2],
                "h_level": row[3],
                "page_numbers": list(range(row[1], row[1] + row[2]))
            })
        
        return sections
    
    def __del__(self):
        """Cleanup database connection"""
        if hasattr(self, 'db'):
            try:
                self.db.conn.close()
            except:
                pass


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def load_sections(
    section_ids: List[str],
    db_path: str = './v2/manuals.db',
    pdf_path: str = './v2/manuals/'
) -> List[Dict[str, Any]]:
    """
    Quick function to load section content
    
    Args:
        section_ids: List of section IDs like ["RAG_1_45", "RAG_1_50"]
        db_path: Path to database
        pdf_path: Path to PDFs
    
    Returns:
        List of sections with full content
    """
    loader = DocumentLoader(db_path, pdf_path)
    refs = [{"section_id": sid} for sid in section_ids]
    return loader.get_sections_content(refs)


def load_pages(
    manual_id: int,
    page_numbers: List[int],
    db_path: str = './v2/manuals.db',
    pdf_path: str = './v2/manuals/'
) -> str:
    """
    Quick function to load page content
    
    Args:
        manual_id: Manual ID
        page_numbers: List of page numbers
        db_path: Path to database
        pdf_path: Path to PDFs
    
    Returns:
        Combined text from all pages
    """
    loader = DocumentLoader(db_path, pdf_path)
    result = loader.get_pages_content(manual_id, page_numbers)
    return result['combined_text']


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Example 1: Load sections from references
    print("=" * 80)
    print("Example 1: Load sections from references")
    print("=" * 80)
    
    loader = DocumentLoader()
    
    # Simulate getting references from RAG
    section_refs = [
        {"section_id": "RAG_1_45"},
        {"section_id": "RAG_1_50", "include_images": True}
    ]
    
    sections = loader.get_sections_content(section_refs)
    
    for section in sections:
        print(f"\nSection: {section['section_name']}")
        print(f"Pages: {section['page_numbers']}")
        print(f"Text length: {len(section['full_text'])} chars")
        print(f"Images: {section['images']}")
        print(f"Preview: {section['full_text'][:200]}...")
    
    # Example 2: Load specific pages
    print("\n" + "=" * 80)
    print("Example 2: Load specific pages")
    print("=" * 80)
    
    pages_content = loader.get_pages_content(
        manual_id=1,
        page_numbers=[45, 46]
    )
    
    print(f"Loaded {len(pages_content['pages'])} pages")
    print(f"Combined text length: {len(pages_content['combined_text'])} chars")
    print(f"Preview: {pages_content['combined_text'][:200]}...")
    
    # Example 3: Get single page
    print("\n" + "=" * 80)
    print("Example 3: Get single page")
    print("=" * 80)
    
    page_text = loader.get_page_content(manual_id=1, page_number=45)
    print(f"Page 45 text length: {len(page_text)} chars")
    print(f"Preview: {page_text[:200]}...")
    
    # Example 4: Search by section name
    print("\n" + "=" * 80)
    print("Example 4: Search by section name")
    print("=" * 80)
    
    section = loader.get_section_by_name(manual_id=1, section_name="Oil")
    if section:
        print(f"Found: {section['section_name']}")
        print(f"Pages: {section['page_numbers']}")
    else:
        print("Section not found")
    
    # Example 5: List all sections
    print("\n" + "=" * 80)
    print("Example 5: List all sections in manual")
    print("=" * 80)
    
    sections = loader.list_sections(manual_id=1)
    print(f"Found {len(sections)} sections:")
    for s in sections[:5]:  # Show first 5
        print(f"  - {s['section_name']} (pages {s['first_page']}-{s['first_page']+s['length']-1})")
    
    # Example 6: Convenience functions
    print("\n" + "=" * 80)
    print("Example 6: Convenience functions")
    print("=" * 80)
    
    # Quick load
    sections = load_sections(["RAG_1_45"])
    print(f"Loaded {len(sections)} sections using convenience function")
    
    pages = load_pages(manual_id=1, page_numbers=[45, 46])
    print(f"Loaded pages, text length: {len(pages)} chars")
    
    print("\n" + "=" * 80)
    print("Done!")
    print("=" * 80)