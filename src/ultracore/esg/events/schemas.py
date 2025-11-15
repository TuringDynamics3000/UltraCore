"""
ESG Event Schemas for Kafka Topics

This module defines the event schemas for the ESG module's Kafka topics.
We use Python dataclasses with type hints to define the schema, which can
be easily serialized to JSON or Avro format.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum


class EsgProvider(str, Enum):
    """ESG data providers"""
    MSCI = "MSCI"
    SUSTAINALYTICS = "Sustainalytics"
    BLOOMBERG = "Bloomberg"
    REFINITIV = "Refinitiv"
    FTSE_RUSSELL = "FTSE_Russell"


class EsgMetricType(str, Enum):
    """Types of ESG metrics"""
    RATING = "rating"  # Overall ESG rating (e.g., AAA-CCC)
    SCORE = "score"  # Numerical score (0-100)
    CARBON_INTENSITY = "carbon_intensity"  # tCO2e per $M revenue
    WATER_INTENSITY = "water_intensity"  # m3 per $M revenue
    WASTE_INTENSITY = "waste_intensity"  # tonnes per $M revenue
    BOARD_DIVERSITY = "board_diversity"  # % women on board
    EMPLOYEE_TURNOVER = "employee_turnover"  # % annual turnover
    CONTROVERSY_SCORE = "controversy_score"  # 0-10 scale
    SDG_ALIGNMENT = "sdg_alignment"  # UN SDG alignment score


class PortfolioEventType(str, Enum):
    """Types of portfolio events"""
    ESG_PREFERENCE_SET = "esg_preference_set"
    EXCLUSION_LIST_UPDATED = "exclusion_list_updated"
    PORTFOLIO_REBALANCED = "portfolio_rebalanced"
    ESG_CONSTRAINT_ADDED = "esg_constraint_added"
    ESG_CONSTRAINT_REMOVED = "esg_constraint_removed"
    PORTFOLIO_OPTIMIZATION_REQUESTED = "portfolio_optimization_requested"
    PORTFOLIO_OPTIMIZATION_COMPLETED = "portfolio_optimization_completed"


class CorporateActionType(str, Enum):
    """Types of corporate actions with ESG implications"""
    GREEN_BOND_ISSUED = "green_bond_issued"
    CARBON_NEUTRAL_PLEDGE = "carbon_neutral_pledge"
    RENEWABLE_ENERGY_TARGET = "renewable_energy_target"
    ESG_CONTROVERSY = "esg_controversy"
    SUSTAINABILITY_REPORT_PUBLISHED = "sustainability_report_published"


@dataclass
class EsgDataRawEvent:
    """Raw, unprocessed ESG data from external providers"""
    source: str  # Provider name
    timestamp: datetime
    payload: Dict[str, Any]  # Raw JSON payload from provider
    ingestion_id: str = field(default_factory=lambda: str(datetime.now().timestamp()))


@dataclass
class EsgDataNormalizedEvent:
    """Standardized ESG data point"""
    isin: str  # International Securities Identification Number
    timestamp: datetime
    provider: EsgProvider
    metric_type: EsgMetricType
    metric_value: float
    metric_unit: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(datetime.now().timestamp()))


@dataclass
class EsgPortfolioEvent:
    """Events related to portfolio ESG configuration"""
    portfolio_id: str
    timestamp: datetime
    event_type: PortfolioEventType
    payload: Dict[str, Any]
    user_id: Optional[str] = None
    event_id: str = field(default_factory=lambda: str(datetime.now().timestamp()))


@dataclass
class EsgPreference:
    """ESG preference for a portfolio or investor"""
    min_esg_rating: Optional[str] = None  # e.g., "A" or higher
    max_carbon_intensity: Optional[float] = None  # tCO2e per $M revenue
    excluded_sectors: List[str] = field(default_factory=list)  # e.g., ["Tobacco", "Weapons"]
    sdg_alignment_targets: Dict[int, float] = field(default_factory=dict)  # SDG number -> target score
    esg_weight: float = 0.5  # Weight of ESG vs financial objectives (0-1)


@dataclass
class EsgCorporateActionEvent:
    """Corporate actions with ESG implications"""
    isin: str
    timestamp: datetime
    action_type: CorporateActionType
    description: str
    impact_score: Optional[float] = None  # Estimated impact on ESG rating (-10 to +10)
    source_url: Optional[str] = None
    event_id: str = field(default_factory=lambda: str(datetime.now().timestamp()))


@dataclass
class EsgRegulatoryUpdateEvent:
    """Updates to ESG regulations"""
    jurisdiction: str  # e.g., "EU", "US", "AU"
    timestamp: datetime
    regulation_name: str  # e.g., "SFDR", "CSRD", "TCFD"
    summary: str
    effective_date: Optional[datetime] = None
    source_url: Optional[str] = None
    event_id: str = field(default_factory=lambda: str(datetime.now().timestamp()))


# Kafka topic names
TOPIC_ESG_DATA_RAW = "esg-data-raw"
TOPIC_ESG_DATA_NORMALIZED = "esg-data-normalized"
TOPIC_ESG_PORTFOLIO_EVENTS = "esg-portfolio-events"
TOPIC_ESG_CORPORATE_ACTIONS = "esg-corporate-actions"
TOPIC_ESG_REGULATORY_UPDATES = "esg-regulatory-updates"
