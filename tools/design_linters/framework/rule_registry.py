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
import inspect
import logging
import pkgutil
from pathlib import Path
from typing import Any

from .interfaces import LintRule, RuleRegistry


class DefaultRuleRegistry(RuleRegistry):
    """Default implementation of rule registry with plugin discovery."""

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._rules: dict[str, LintRule] = {}
        self._rules_by_category: dict[str, set[str]] = {}
        self._logger = logging.getLogger(__name__)

    def register_rule(self, rule: LintRule) -> None:
        """Register a new rule."""
        rule_id = rule.rule_id

        if rule_id in self._rules:
            self._logger.warning("Rule %s already registered, overriding", rule_id)

        self._rules[rule_id] = rule

        # Update category index
        for category in rule.categories:
            if category not in self._rules_by_category:
                self._rules_by_category[category] = set()
            self._rules_by_category[category].add(rule_id)

        self._logger.debug("Registered rule: %s", rule_id)

    def unregister_rule(self, rule_id: str) -> None:
        """Unregister a rule by ID."""
        if rule_id not in self._rules:
            self._logger.warning("Rule %s not found for unregistration", rule_id)
            return

        rule = self._rules[rule_id]

        # Remove from category index
        for category in rule.categories:
            if category in self._rules_by_category:
                self._rules_by_category[category].discard(rule_id)
                if not self._rules_by_category[category]:
                    del self._rules_by_category[category]

        del self._rules[rule_id]
        self._logger.debug("Unregistered rule: %s", rule_id)

    def get_rule(self, rule_id: str) -> LintRule | None:
        """Get a rule by ID."""
        return self._rules.get(rule_id)

    def get_all_rules(self) -> list[LintRule]:
        """Get all registered rules."""
        return list(self._rules.values())

    def get_rules_by_category(self, category: str) -> list[LintRule]:
        """Get rules belonging to a specific category."""
        rule_ids = self._rules_by_category.get(category, set())
        return [self._rules[rule_id] for rule_id in rule_ids if rule_id in self._rules]

    def get_rule_count(self) -> int:
        """Get total number of registered rules."""
        return len(self._rules)

    def get_categories(self) -> set[str]:
        """Get all available rule categories."""
        return set(self._rules_by_category.keys())

    def get_rule_info(self) -> dict[str, dict[str, Any]]:
        """Get summary information about all rules."""
        return {
            rule_id: {
                "name": rule.rule_name,
                "description": rule.description,
                "severity": rule.severity.value,
                "categories": list(rule.categories),
            }
            for rule_id, rule in self._rules.items()
        }

    def discover_rules(self, package_paths: list[str]) -> int:
        """Discover and register rules from package paths."""
        discovered_count = 0
        discovery_service = RuleDiscoveryService(self._logger)

        for package_path in package_paths:
            try:
                count = discovery_service.discover_from_package(package_path, self)
                discovered_count += count
                self._logger.info("Discovered %d rules from %s", count, package_path)
            except Exception as e:  # pylint: disable=broad-exception-caught
                self._logger.error("Error discovering rules from %s: %s", package_path, e)

        return discovered_count


class RuleDiscoveryService:
    """Service for discovering rules from packages and modules."""

    def __init__(self, logger: logging.Logger | None = None):
        """Initialize discovery service."""
        self._logger = logger or logging.getLogger(__name__)

    def discover_from_package(self, package_path: str, registry: RuleRegistry) -> int:
        """Discover rules from a package and register them."""
        discovered_count = 0

        try:
            # Import the package
            package = importlib.import_module(package_path)

            # Walk through all modules in the package
            if hasattr(package, "__path__"):
                for _, module_name, _ in pkgutil.iter_modules(package.__path__):
                    full_module_name = f"{package_path}.{module_name}"
                    try:
                        count = self._discover_from_module(full_module_name, registry)
                        discovered_count += count
                    except (ImportError, AttributeError, ValueError) as e:
                        self._logger.warning("Error importing module %s: %s", full_module_name, e)
            else:
                # Single module
                count = self._discover_from_module(package_path, registry)
                discovered_count += count

        except ImportError as e:
            self._logger.error("Could not import package %s: %s", package_path, e)
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
                        self._logger.debug("Discovered rule: %s", rule_instance.rule_id)
                    except (TypeError, AttributeError, ValueError) as e:
                        self._logger.warning("Error instantiating rule %s: %s", name, e)

        except (ImportError, AttributeError) as e:
            self._logger.warning("Error processing module %s: %s", module_path, e)

        return discovered_count

    def _is_rule_class(self, obj: Any) -> bool:
        """Check if an object is a valid rule class."""
        return (
            inspect.isclass(obj)
            and issubclass(obj, LintRule)
            and obj is not LintRule  # Don't instantiate the base class
            and not inspect.isabstract(obj)
        )  # Don't instantiate abstract classes

    def discover_from_directory(self, directory_path: Path, registry: RuleRegistry) -> int:
        """Discover rules from Python files in a directory."""
        discovered_count = 0

        for py_file in directory_path.rglob("*.py"):
            if py_file.name.startswith("__") or py_file.name.startswith("test_"):
                continue

            try:
                count = self._discover_from_file(py_file, registry)
                discovered_count += count
            except (ImportError, AttributeError, OSError) as e:
                self._logger.warning("Error discovering from %s: %s", py_file, e)

        return discovered_count

    def _discover_from_file(self, file_path: Path, registry: RuleRegistry) -> int:
        """Discover rules from a specific Python file."""
        # This is more complex as it requires dynamic module loading
        # For now, we'll focus on package-based discovery
        # Could be implemented using importlib.util.spec_from_file_location
        # Parameters are kept for future implementation
        del file_path, registry  # Mark as intentionally unused
        return 0


class CategorizedRuleRegistry(DefaultRuleRegistry):
    """Extended rule registry with advanced categorization features."""

    def __init__(self) -> None:
        """Initialize with category management features."""
        super().__init__()
        self._category_metadata: dict[str, dict[str, Any]] = {}

    def register_category(self, category: str, description: str, priority: int = 0) -> None:
        """Register metadata for a category."""
        self._category_metadata[category] = {
            "description": description,
            "priority": priority,
            "rule_count": len(self._rules_by_category.get(category, set())),
        }

    def get_category_info(self, category: str) -> dict[str, Any] | None:
        """Get information about a category."""
        if category in self._category_metadata:
            info = self._category_metadata[category].copy()
            info["rule_count"] = len(self._rules_by_category.get(category, set()))
            return info
        return None

    def get_categories_by_priority(self) -> list[str]:
        """Get categories sorted by priority."""
        return sorted(
            self._category_metadata.keys(),
            key=lambda cat: self._category_metadata[cat].get("priority", 0),
            reverse=True,
        )

    def get_rules_summary(self) -> dict[str, Any]:
        """Get comprehensive summary of all rules and categories."""
        return {
            "total_rules": len(self._rules),
            "total_categories": len(self._rules_by_category),
            "categories": {
                cat: {
                    "rule_count": len(rule_ids),
                    "rules": list(rule_ids),
                    "metadata": self._category_metadata.get(cat, {}),
                }
                for cat, rule_ids in self._rules_by_category.items()
            },
            "uncategorized_rules": [rule_id for rule_id, rule in self._rules.items() if not rule.categories],
        }
