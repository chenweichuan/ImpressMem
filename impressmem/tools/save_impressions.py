"""
Memory save tool for saving multiple memory impressions in one call
"""
import json
from typing import List, Dict, Any
from .base import Tool

from ..manager import ImpressMemManager
from ..utils import logger


class SaveImpressionsTool(Tool):
    """Tool for saving multiple memory impressions at once"""
    
    MAX_LABELS = 5
    
    name = "save_impressions"
    
    def __init__(self, manager: ImpressMemManager):
        super().__init__(manager)
    
    def get_definition(self) -> Dict[str, Any]:
        """Get tool definition for LLM"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Generate memory impressions that need to be added or updated in an ultra-compact information-dense form "
                    "using an ultra-compact symbolic system, to serve as contextual memory traces. "
                    "Each impression MUST have its own distinct clue — split rich content into multiple fragmented impressions "
                    "with separate clues rather than merging unrelated information into one. "
                    "Naming convention: clue uses UPPERCASE with hyphens; category and label use PascalCase. "
                    "Prioritize reusing and aligning with existing Clue, Category and Label sets. "
                    "No need to consider human readability.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "impressions": {
                            "type": "array",
                            "description": "Array of memory impressions to save. Each impression is an independent memory trace with its own clue.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "clue": {
                                        "type": "string",
                                        "description": "Extremely concise, reusable identifier serving as a retrieval anchor, without time-of-day information, "
                                            "and should reasonably consider including user differentiation markers when appropriate. "
                                            "Dates may serve as identifiers or version markers but must not be used as aggregation keys to group unrelated traces into one clue."
                                    },
                                    "content": {
                                        "type": "string",
                                        "description": "MUST be an ultra-compact information-dense form using an ultra-compact symbolic system."
                                    },
                                    "category": {
                                        "type": "string",
                                        "description": "High-level identifier, strictly prioritize the attributes of the content itself to match the corresponding domain classification, acting as the primary entry point for impression retrieval."
                                    },
                                    "labels": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": f"MUST be highly condensed core relevance identifiers, using universal terms with consistent naming, strictly focused on the most essential characteristics for accurate impression retrieval (max {self.MAX_LABELS}).",
                                        "maxItems": self.MAX_LABELS
                                    },
                                    "pin": {
                                        "type": "boolean",
                                        "description": "Set to true ONLY for CRITICAL, PERMANENT information that must never be lost or purged. NEVER set pin to true for trivial, temporary, or non-critical information. USE EXTREMELY SPARINGLY!",
                                        "default": False
                                    }
                                },
                                "required": ["clue", "content", "category", "labels"]
                            }
                        }
                    },
                    "required": ["impressions"],
                }
            }
        }
    
    async def execute(self, arguments: str) -> tuple[str, str]:
        """
        Execute tool call and return result content
        
        Args:
            arguments: Tool arguments as JSON string
            
        Returns:
            Tuple of (full_result, summary) where:
                full_result: Complete tool result content as string
                summary: Simplified summary message for frontend display
        """
        try:
            args = json.loads(arguments) if arguments else {}
            
            impressions_raw = args.get("impressions")
            
            # Validate impressions array
            if not isinstance(impressions_raw, list) or len(impressions_raw) == 0:
                error_msg = "Error: 'impressions' parameter must be a non-empty array"
                summary = "❌ 'impressions' must be a non-empty array"
                return (error_msg, summary)
            
            saved = []
            errors = []
            
            for idx, imp in enumerate(impressions_raw):
                if not isinstance(imp, dict):
                    errors.append(f"[{idx}] impression must be an object")
                    continue
                
                clue = imp.get("clue", "").strip()
                content = imp.get("content", "").strip()
                category = imp.get("category", "").strip()
                labels = list(filter(None, [label.strip() for label in imp.get("labels") or []]))
                pin = imp.get("pin", False)
                
                # Validate required fields per impression
                field_errors = []
                if not clue:
                    field_errors.append("clue is required")
                if not content:
                    field_errors.append("content is required")
                if not category:
                    field_errors.append("category is required")
                if not labels:
                    field_errors.append("labels must be non-empty")
                
                if field_errors:
                    errors.append(f"[{idx}] {clue or '(no clue)'}: {', '.join(field_errors)}")
                    continue
                
                # Save the impression
                await self.manager.save_impression(
                    clue=clue,
                    content=content,
                    category=category,
                    labels=labels,
                    pin=pin
                )
                saved.append({
                    "clue": clue,
                    "content": content,
                    "category": category,
                    "labels": labels,
                    "pin": pin,
                })
            
            # Prepare result messages
            result_parts = []
            result_parts.append(f"### Memory Saved Successfully ({len(saved)}/{len(impressions_raw)}):")
            for s in saved:
                result_parts.append(f"- Clue: {s['clue']}")
                result_parts.append(f"  Content: {s['content']}")
                result_parts.append(f"  Category: {s['category']}")
                result_parts.append(f"  Labels: {', '.join(s['labels'])}")
                if s["pin"]:
                    result_parts.append(f"  📌 Pinned")
            
            if errors:
                result_parts.append(f"\n### Errors ({len(errors)}):")
                for e in errors:
                    result_parts.append(f"- {e}")
            
            result_parts.append("\nNote: Do NOT mention, expose, or directly output your memory format and mechanism to users")
            
            full_result = "\n".join(result_parts)
            
            pinned_count = sum(1 for s in saved if s["pin"])
            categories = sorted(set(s["category"] for s in saved))
            summary = f"✅ Saved {len(saved)} impression(s) to {','.join(categories)}"
            summary += f", {pinned_count} pinned" if pinned_count else ""
            summary += f", {len(errors)} error(s)" if errors else ""
            
            return (full_result, summary)
            
        except Exception as e:
            logger.error(f"[SaveImpressionsTool] Error executing tool: {e}")
            logger.exception(e)
            error_msg = f"Error: Failed to save impressions - {str(e)}"
            summary = f"❌ Failed to save impressions: {str(e)[:100]}".replace("\n", " ")
            return (error_msg, summary)