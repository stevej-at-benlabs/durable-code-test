#!/usr/bin/env python3
"""
Purpose: Rule registry for managing and discovering linting rules
Scope: Provides dynamic registration and discovery of linting rules
Overview: This module implements a pluggable rule registry that allows
    dynamic registration, discovery, and management of linting rules.
    It supports automatic discovery from packages, categorization,
    and runtime rule management for a flexible plugin architecture.
Dependencies: importlib for dynamic imports, pkgutil for package discovery
Exports: DefaultRuleRegistry, RuleDiscoveryService
Interfaces: Implements RuleRegistry interface
Implementation: Plugin architecture with automatic discovery capabilities
"""

import importlib
import pkgutil
import inspect
from typing import List, Dict, Set, Optional, Type
from pathlib import Path
import logging

from .interfaces import LintRule, RuleRegistry


class DefaultRuleRegistry(RuleRegistry):
    """Default implementation of rule registry with plugin discovery."""

    def __init__(self):
        """Initialize empty registry."""
        self._rules: Dict[str, LintRule] = {}
        self._rules_by_category: Dict[str, Set[str]] = {}
        self._logger = logging.getLogger(__name__)

    def register_rule(self, rule: LintRule) -> None:
        """Register a new rule."""
        rule_id = rule.rule_id

        if rule_id in self._rules:
            self._logger.warning(f"Rule {rule_id} already registered, overriding")

        self._rules[rule_id] = rule

        # Update category index
        for category in rule.categories:
            if category not in self._rules_by_category:
                self._rules_by_category[category] = set()
            self._rules_by_category[category].add(rule_id)

        self._logger.debug(f"Registered rule: {rule_id}")

    def unregister_rule(self, rule_id: str) -> None:
        """Unregister a rule by ID."""
        if rule_id not in self._rules:
            self._logger.warning(f"Rule {rule_id} not found for unregistration")
            return

        rule = self._rules[rule_id]

        # Remove from category index
        for category in rule.categories:
            if category in self._rules_by_category:
                self._rules_by_category[category].discard(rule_id)
                if not self._rules_by_category[category]:
                    del self._rules_by_category[category]

        del self._rules[rule_id]
        self._logger.debug(f"Unregistered rule: {rule_id}")

    def get_rule(self, rule_id: str) -> Optional[LintRule]:
        """Get a rule by ID."""
        return self._rules.get(rule_id)

    def get_all_rules(self) -> List[LintRule]:
        """Get all registered rules."""
        return list(self._rules.values())

    def get_rules_by_category(self, category: str) -> List[LintRule]:
        """Get rules belonging to a specific category."""
        rule_ids = self._rules_by_category.get(category, set())
        return [self._rules[rule_id] for rule_id in rule_ids if rule_id in self._rules]

    def get_rule_count(self) -> int:
        """Get total number of registered rules."""
        return len(self._rules)

    def get_categories(self) -> Set[str]:
        """Get all available rule categories."""
        return set(self._rules_by_category.keys())

    def get_rule_info(self) -> Dict[str, Dict[str, any]]:
        """Get summary information about all rules."""
        return {
            rule_id: {
                'name': rule.rule_name,
                'description': rule.description,
                'severity': rule.severity.value,
                'categories': list(rule.categories)
            }
            for rule_id, rule in self._rules.items()
        }

    def discover_rules(self, package_paths: List[str]) -> int:
        """Discover and register rules from package paths."""
        discovered_count = 0
        discovery_service = RuleDiscoveryService(self._logger)

        for package_path in package_paths:
            try:
                count = discovery_service.discover_from_package(package_path, self)
                discovered_count += count
                self._logger.info(f"Discovered {count} rules from {package_path}")
            except Exception as e:
                self._logger.error(f"Error discovering rules from {package_path}: {e}")

        return discovered_count


class RuleDiscoveryService:
    """Service for discovering rules from packages and modules."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize discovery service."""
        self._logger = logger or logging.getLogger(__name__)

    def discover_from_package(self, package_path: str, registry: RuleRegistry) -> int:
        """Discover rules from a package and register them."""
        discovered_count = 0

        try:
            # Import the package
            package = importlib.import_module(package_path)

            # Walk through all modules in the package
            if hasattr(package, '__path__'):
                for _, module_name, _ in pkgutil.iter_modules(package.__path__):
                    full_module_name = f"{package_path}.{module_name}"
                    try:
                        count = self._discover_from_module(full_module_name, registry)
                        discovered_count += count
                    except Exception as e:
                        self._logger.warning(f"Error importing module {full_module_name}: {e}")
            else:
                # Single module
                count = self._discover_from_module(package_path, registry)
                discovered_count += count

        except ImportError as e:
            self._logger.error(f"Could not import package {package_path}: {e}")
            raise

        return discovered_count

    def _discover_from_module(self, module_path: str, registry: RuleRegistry) -> int:
        """Discover rules from a specific module."""
        discovered_count = 0

        try:
            module = importlib.import_module(module_path)

            # Look for rule classes in the module
            for name, obj in inspect.getmembers(module):
                if self._is_rule_class(obj):
                    try:
                        # Instantiate the rule
                        rule_instance = obj()
                        registry.register_rule(rule_instance)
                        discovered_count += 1
                        self._logger.debug(f"Discovered rule: {rule_instance.rule_id}")
                    except Exception as e:
                        self._logger.warning(f"Error instantiating rule {name}: {e}")

        except Exception as e:
            self._logger.warning(f"Error processing module {module_path}: {e}")

        return discovered_count

    def _is_rule_class(self, obj: any) -> bool:
        """Check if an object is a valid rule class."""
        return (inspect.isclass(obj) and
                issubclass(obj, LintRule) and
                obj is not LintRule and  # Don't instantiate the base class
                not inspect.isabstract(obj))  # Don't instantiate abstract classes

    def discover_from_directory(self, directory_path: Path, registry: RuleRegistry) -> int:
        """Discover rules from Python files in a directory."""
        discovered_count = 0

        for py_file in directory_path.rglob('*.py'):
            if py_file.name.startswith('__') or py_file.name.startswith('test_'):
                continue

            try:
                count = self._discover_from_file(py_file, registry)
                discovered_count += count
            except Exception as e:
                self._logger.warning(f"Error discovering from {py_file}: {e}")

        return discovered_count

    def _discover_from_file(self, file_path: Path, registry: RuleRegistry) -> int:
        """Discover rules from a specific Python file."""
        # This is more complex as it requires dynamic module loading
        # For now, we'll focus on package-based discovery
        # Could be implemented using importlib.util.spec_from_file_location
        return 0


class CategorizedRuleRegistry(DefaultRuleRegistry):
    """Extended rule registry with advanced categorization features."""

    def __init__(self):
        """Initialize with category management features."""
        super().__init__()
        self._category_metadata: Dict[str, Dict[str, any]] = {}

    def register_category(self, category: str, description: str,
                         priority: int = 0) -> None:
        """Register metadata for a category."""
        self._category_metadata[category] = {
            'description': description,
            'priority': priority,
            'rule_count': len(self._rules_by_category.get(category, set()))
        }

    def get_category_info(self, category: str) -> Optional[Dict[str, any]]:
        """Get information about a category."""
        if category in self._category_metadata:
            info = self._category_metadata[category].copy()
            info['rule_count'] = len(self._rules_by_category.get(category, set()))
            return info
        return None

    def get_categories_by_priority(self) -> List[str]:
        """Get categories sorted by priority."""
        return sorted(
            self._category_metadata.keys(),
            key=lambda cat: self._category_metadata[cat].get('priority', 0),
            reverse=True
        )

    def get_rules_summary(self) -> Dict[str, any]:
        """Get comprehensive summary of all rules and categories."""
        return {
            'total_rules': len(self._rules),
            'total_categories': len(self._rules_by_category),
            'categories': {
                cat: {
                    'rule_count': len(rule_ids),
                    'rules': list(rule_ids),
                    'metadata': self._category_metadata.get(cat, {})
                }
                for cat, rule_ids in self._rules_by_category.items()
            },
            'uncategorized_rules': [
                rule_id for rule_id, rule in self._rules.items()
                if not rule.categories
            ]
        }
