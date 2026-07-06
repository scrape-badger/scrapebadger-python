"""Pydantic models for Zillow API responses.

These models mirror the backend ``zillow_scraper`` response schema
field-for-field. All models are immutable (frozen) and ignore unknown fields
for forward compatibility. Every datetime field ships in BOTH ``*_utc`` (Unix
float) and ``*_at`` (ISO-8601 Z string).

Zillow is a single-domain, single-locale target (zillow.com, USD, en-US); US +
Canadian inventory are both served from zillow.com behind a US IP, so there is
no market/currency dimension on the models.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# =============================================================================
# Base Configuration
# =============================================================================


class _BaseModel(BaseModel):
    """Base model with common configuration."""

    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True,
        extra="ignore",
    )


# =============================================================================
# Shared / nested models
# =============================================================================


class LatLong(_BaseModel):
    """A latitude/longitude pair."""

    latitude: float | None = None
    longitude: float | None = None


class Photo(_BaseModel):
    """A single listing photo with its responsive source variants."""

    url: str | None = None
    caption: str | None = None
    subject_type: str | None = None
    # Responsive variants: [{"url": ..., "width": ..., "format": "jpeg"|"webp"}]
    sources: list[dict[str, Any]] = Field(default_factory=list)


class Pagination(_BaseModel):
    """Page-number pagination (Zillow search returns ~40 results per page)."""

    current_page: int = 1
    per_page: int | None = None
    total_pages: int | None = None
    total_results: int | None = None


class MapBounds(_BaseModel):
    """The map bounding box a search covers — callers tile with this to beat
    Zillow's ~820-result (20-page) cap by subdividing dense boxes."""

    north: float | None = None
    east: float | None = None
    south: float | None = None
    west: float | None = None


class RegionSelection(_BaseModel):
    """The numeric region a search resolved to (region_id + region_type)."""

    region_id: int | None = None
    region_type: int | None = None


class NearbyRegion(_BaseModel):
    """A linked nearby region (city / neighborhood / zip) on a property page."""

    name: str | None = None
    region_type: str | None = None
    url: str | None = None


class MarketInfo(_BaseModel):
    """A supported coverage region (for /markets)."""

    code: str
    country: str
    currency: str
    locale: str
    name: str
    domain: str


# =============================================================================
# Search results
# =============================================================================


class Listing(_BaseModel):
    """One Zillow search card (search / agent listings).

    Merges the search ``listResult`` top-level with its richer
    ``hdpData.homeInfo`` sub-object.
    """

    position: int
    zpid: str | None = None
    id: str | None = None
    detail_url: str | None = None
    # Status / type
    home_type: str | None = None  # SINGLE_FAMILY, CONDO, TOWNHOUSE, APARTMENT …
    home_status: str | None = None  # FOR_SALE, FOR_RENT, SOLD, PENDING …
    status_text: str | None = None  # "House for sale"
    status_type: str | None = None
    marketing_status: str | None = None
    contingent_listing_type: str | None = None
    # Price / valuation
    price: int | None = None
    price_raw: str | None = None  # "$460,000" / "$2,400/mo"
    currency: str | None = None
    price_change: int | None = None
    date_price_changed_utc: float | None = None
    date_price_changed_at: str | None = None
    price_reduction: str | None = None
    flex_field_text: str | None = None  # marketing badge ("Price cut", "$X (Nov 1)")
    zestimate: int | None = None
    rent_zestimate: int | None = None
    tax_assessed_value: int | None = None
    # Specs
    beds: float | None = None
    baths: float | None = None
    living_area: int | None = None
    lot_area_value: float | None = None
    lot_area_unit: str | None = None
    # Address
    address: str | None = None
    street_address: str | None = None
    unit: str | None = None
    city: str | None = None
    state: str | None = None
    zipcode: str | None = None
    country: str | None = None
    is_undisclosed_address: bool | None = None
    latitude: float | None = None
    longitude: float | None = None
    # Listing meta
    broker_name: str | None = None
    provider_listing_id: str | None = None
    days_on_zillow: int | None = None
    is_zillow_owned: bool | None = None
    is_featured: bool | None = None
    is_showcase: bool | None = None
    is_fsba: bool | None = None  # for-sale-by-agent (from listing_sub_type)
    is_new_construction: bool | None = None
    is_premier_builder: bool | None = None
    is_preforeclosure_auction: bool | None = None
    is_non_owner_occupied: bool | None = None
    # Media
    img_src: str | None = None
    has_image: bool | None = None
    has_video: bool | None = None
    has_3d_model: bool | None = None
    has_open_house: bool | None = None
    open_house_start: str | None = None
    open_house_end: str | None = None
    photos: list[str] = Field(default_factory=list)


# =============================================================================
# Property detail nested
# =============================================================================


class Address(_BaseModel):
    """A property street address (property-detail block)."""

    street_address: str | None = None
    city: str | None = None
    state: str | None = None
    zipcode: str | None = None
    community: str | None = None
    subdivision: str | None = None
    neighborhood: str | None = None


class ListingSubType(_BaseModel):
    """``listingSubType`` flags — the for-sale / foreclosure / auction taxonomy."""

    is_fsba: bool | None = None  # for sale by agent
    is_fsbo: bool | None = None  # for sale by owner
    is_foreclosure: bool | None = None
    is_bank_owned: bool | None = None
    is_for_auction: bool | None = None
    is_coming_soon: bool | None = None
    is_new_home: bool | None = None
    is_pending: bool | None = None


class OpenHouse(_BaseModel):
    """A single scheduled open house."""

    start_utc: float | None = None
    start_at: str | None = None
    end_utc: float | None = None
    end_at: str | None = None
    note: str | None = None


class ZestimateHistoryPoint(_BaseModel):
    """One point in the Zestimate value history series (``homeValueChartData``)."""

    date: str | None = None
    date_utc: float | None = None
    date_at: str | None = None
    value: int | None = None


class PriceHistoryEvent(_BaseModel):
    """A single price-history event (listing, sale, price change)."""

    date: str | None = None
    date_utc: float | None = None
    date_at: str | None = None
    event: str | None = None  # "Listed for sale", "Price change", "Sold" …
    price: int | None = None
    price_per_square_foot: int | None = None
    price_change_rate: float | None = None
    source: str | None = None
    buyer_agent: str | None = None
    seller_agent: str | None = None
    posting_is_rental: bool | None = None


class TaxHistoryEvent(_BaseModel):
    """A single year of tax/assessment history."""

    year_utc: float | None = None
    year_at: str | None = None
    value: int | None = None
    value_increase_rate: float | None = None
    tax_paid: float | None = None
    tax_increase_rate: float | None = None


class School(_BaseModel):
    """A school associated with a property."""

    name: str | None = None
    rating: int | None = None
    grades: str | None = None
    level: str | None = None  # Elementary / Middle / High / Primary
    type: str | None = None  # Public / Private / Charter
    distance: float | None = None
    link: str | None = None
    student_count: int | None = None
    assigned: bool | None = None


class AgentAttribution(_BaseModel):
    """Listing agent / broker attribution (from ``attributionInfo``)."""

    agent_name: str | None = None
    agent_phone: str | None = None
    agent_email: str | None = None
    agent_license_number: str | None = None
    co_agent_name: str | None = None
    co_agent_number: str | None = None
    co_agent_license_number: str | None = None
    broker_name: str | None = None
    broker_phone: str | None = None
    buyer_agent_name: str | None = None
    buyer_brokerage_name: str | None = None
    mls_id: str | None = None
    mls_name: str | None = None
    mls_disclaimer: str | None = None
    listing_agreement: str | None = None
    listing_attribution_contact: str | None = None
    provider_logo: str | None = None
    true_status: str | None = None
    last_checked: str | None = None
    last_updated: str | None = None
    listing_agents: list[dict[str, Any]] = Field(default_factory=list)
    listing_offices: list[dict[str, Any]] = Field(default_factory=list)


class MortgageRate(_BaseModel):
    """A single mortgage-rate quote for a loan product."""

    rate: float | None = None
    rate_source: str | None = None
    last_updated_utc: float | None = None
    last_updated_at: str | None = None


class MortgageRates(_BaseModel):
    """Current mortgage rates by loan product (from ``mortgageRates``)."""

    fifteen_year_fixed: MortgageRate | None = None
    thirty_year_fixed: MortgageRate | None = None
    arm_5: MortgageRate | None = None


class HomeFacts(_BaseModel):
    """High-value subset of Zillow's ``resoFacts`` MLS block.

    resoFacts carries ~187 keys; these are the ones competitors surface and
    callers actually query.
    """

    # Bath breakdown
    bathrooms_full: int | None = None
    bathrooms_half: int | None = None
    bathrooms_three_quarter: int | None = None
    bathrooms_one_quarter: int | None = None
    # Structure
    stories: int | None = None
    stories_decimal: float | None = None
    levels: str | None = None
    property_condition: str | None = None
    architectural_style: str | None = None
    structure_type: str | None = None
    building_name: str | None = None
    construction_materials: list[str] = Field(default_factory=list)
    foundation_details: list[str] = Field(default_factory=list)
    roof_type: str | None = None
    year_built_effective: int | None = None
    # Area breakdown
    above_grade_finished_area: str | None = None
    below_grade_finished_area: str | None = None
    lot_size_dimensions: str | None = None
    main_level_bedrooms: int | None = None
    main_level_bathrooms: int | None = None
    basement: str | None = None
    has_basement: bool | None = None
    attic: str | None = None
    # Systems
    heating: list[str] = Field(default_factory=list)
    cooling: list[str] = Field(default_factory=list)
    appliances: list[str] = Field(default_factory=list)
    flooring: list[str] = Field(default_factory=list)
    utilities: list[str] = Field(default_factory=list)
    electric: list[str] = Field(default_factory=list)
    gas: list[str] = Field(default_factory=list)
    sewer: list[str] = Field(default_factory=list)
    water_source: list[str] = Field(default_factory=list)
    # Green / energy
    green_building_verification_type: list[str] = Field(default_factory=list)
    green_energy_efficient: list[str] = Field(default_factory=list)
    green_energy_generation: list[str] = Field(default_factory=list)
    green_sustainability: list[str] = Field(default_factory=list)
    green_water_conservation: list[str] = Field(default_factory=list)
    # Features
    interior_features: list[str] = Field(default_factory=list)
    exterior_features: list[str] = Field(default_factory=list)
    lot_features: list[str] = Field(default_factory=list)
    community_features: list[str] = Field(default_factory=list)
    accessibility_features: list[str] = Field(default_factory=list)
    door_features: list[str] = Field(default_factory=list)
    window_features: list[str] = Field(default_factory=list)
    laundry_features: list[str] = Field(default_factory=list)
    patio_and_porch_features: list[str] = Field(default_factory=list)
    fencing: list[str] = Field(default_factory=list)
    other_structures: list[str] = Field(default_factory=list)
    view: list[str] = Field(default_factory=list)
    has_view: bool | None = None
    waterfront_features: list[str] = Field(default_factory=list)
    water_view: str | None = None
    water_body_name: str | None = None
    security_features: list[str] = Field(default_factory=list)
    # Parking
    parking_features: list[str] = Field(default_factory=list)
    parking_capacity: int | None = None
    garage_parking_capacity: int | None = None
    carport_parking_capacity: int | None = None
    covered_parking_capacity: int | None = None
    open_parking_capacity: int | None = None
    has_attached_garage: bool | None = None
    has_garage: bool | None = None
    has_carport: bool | None = None
    has_open_parking: bool | None = None
    # Amenities
    pool_features: list[str] = Field(default_factory=list)
    has_private_pool: bool | None = None
    spa_features: list[str] = Field(default_factory=list)
    fireplaces: int | None = None
    fireplace_features: list[str] = Field(default_factory=list)
    has_fireplace: bool | None = None
    # HOA / fees / tax
    association_name: str | None = None
    association_name2: str | None = None
    association_fee: str | None = None
    association_fee2: str | None = None
    association_fee_includes: list[str] = Field(default_factory=list)
    association_amenities: list[str] = Field(default_factory=list)
    association_phone: str | None = None
    has_association: bool | None = None
    hoa_fee: str | None = None
    hoa_fee_total: str | None = None
    tax_annual_amount: float | None = None
    price_per_square_foot: int | None = None
    # Land / lease
    has_land_lease: bool | None = None
    land_lease_amount: str | None = None
    land_lease_expiration_date: str | None = None
    can_raise_horses: bool | None = None
    additional_parcels_description: str | None = None
    road_surface_type: list[str] = Field(default_factory=list)
    # Market timing
    on_market_date: str | None = None
    cumulative_days_on_market: int | None = None
    offer_review_date: str | None = None
    # Rental / multi-unit
    number_of_units_in_community: int | None = None
    availability_date: str | None = None
    lease_term: str | None = None
    tenant_pays: list[str] = Field(default_factory=list)
    has_pets_allowed: bool | None = None
    pets_max_weight: int | None = None
    has_rent_control: bool | None = None
    # Schools (as named on the MLS record)
    elementary_school: str | None = None
    middle_school: str | None = None
    high_school: str | None = None
    elementary_school_district: str | None = None
    middle_school_district: str | None = None
    high_school_district: str | None = None
    # Parcel / legal
    parcel_number: str | None = None
    subdivision_name: str | None = None
    municipality: str | None = None
    city_region: str | None = None
    zoning: str | None = None
    zoning_description: str | None = None
    ownership: str | None = None
    ownership_type: str | None = None
    property_sub_type: list[str] = Field(default_factory=list)
    special_listing_conditions: str | None = None
    listing_terms: str | None = None
    inclusions: str | None = None
    exclusions: str | None = None
    # Flags
    is_new_construction: bool | None = None
    is_senior_community: bool | None = None
    has_home_warranty: bool | None = None
    furnished: bool | None = None
    development_status: str | None = None
    park_name: str | None = None
    # Bulk fact lists Zillow ships verbatim (label/value pairs)
    at_a_glance_facts: list[dict[str, Any]] = Field(default_factory=list)
    rooms: list[dict[str, Any]] = Field(default_factory=list)


# =============================================================================
# Property
# =============================================================================


class Property(_BaseModel):
    """Full Zillow property detail (from ``gdpClientCache[...].property``)."""

    # Identity
    zpid: str
    id: str | None = None
    url: str | None = None
    home_status: str | None = None
    home_type: str | None = None
    property_type: str | None = None
    listing_type: str | None = None
    posting_product_type: str | None = None
    listing_data_source: str | None = None
    mls_id: str | None = None
    parcel_id: str | None = None
    county_fips: str | None = None
    provider_listing_id: str | None = None
    broker_id: str | None = None
    contingent_listing_type: str | None = None
    listing_sub_type: ListingSubType | None = None
    # Price / valuation
    price: int | None = None
    currency: str | None = None
    list_price_low: int | None = None
    monthly_hoa_fee: int | None = None
    property_tax_rate: float | None = None
    annual_homeowners_insurance: int | None = None
    last_sold_price: int | None = None
    date_sold_utc: float | None = None
    date_sold_at: str | None = None
    price_change: int | None = None
    price_change_date_utc: float | None = None
    price_change_date_at: str | None = None
    zestimate: int | None = None
    rent_zestimate: int | None = None
    zestimate_low_percent: str | None = None
    zestimate_high_percent: str | None = None
    rent_zestimate_low_percent: str | None = None
    rent_zestimate_high_percent: str | None = None
    zestimate_30_days_ago: int | None = None
    rent_zestimate_30_days_ago: int | None = None
    tax_assessed_value: int | None = None
    zestimate_history: list[ZestimateHistoryPoint] = Field(default_factory=list)
    # Specs
    bedrooms: float | None = None
    bathrooms: float | None = None
    living_area: int | None = None
    living_area_units: str | None = None
    lot_size: int | None = None
    lot_area_value: float | None = None
    lot_area_units: str | None = None
    year_built: int | None = None
    move_in_ready: bool | None = None
    move_in_completion_date: str | None = None
    # Location
    latitude: float | None = None
    longitude: float | None = None
    street_address: str | None = None
    abbreviated_address: str | None = None
    city: str | None = None
    state: str | None = None
    zipcode: str | None = None
    county: str | None = None
    country: str | None = None
    time_zone: str | None = None
    neighborhood: str | None = None
    is_undisclosed_address: bool | None = None
    is_income_restricted: bool | None = None
    # Engagement
    days_on_zillow: int | None = None
    time_on_zillow: str | None = None
    page_view_count: int | None = None
    favorite_count: int | None = None
    tour_view_count: int | None = None
    photo_count: int | None = None
    # Content
    description: str | None = None
    what_i_love: str | None = None
    home_insights: list[str] = Field(default_factory=list)
    marketing_name: str | None = None
    brokerage_name: str | None = None
    is_showcase_listing: bool | None = None
    has_vr_model: bool | None = None
    has_3d_model: bool | None = None
    virtual_tour_url: str | None = None
    interactive_floor_plan_url: str | None = None
    street_view_image_url: str | None = None
    static_map_url: str | None = None
    new_construction_type: str | None = None
    builder_name: str | None = None
    promotion_headline: str | None = None
    promotion_description: str | None = None
    has_promotion: bool | None = None
    # Nested
    address: Address | None = None
    home_facts: HomeFacts | None = None
    agent: AgentAttribution | None = None
    mortgage_rates: MortgageRates | None = None
    price_history: list[PriceHistoryEvent] = Field(default_factory=list)
    tax_history: list[TaxHistoryEvent] = Field(default_factory=list)
    schools: list[School] = Field(default_factory=list)
    photos: list[Photo] = Field(default_factory=list)
    open_house_schedule: list[OpenHouse] = Field(default_factory=list)
    nearby_cities: list[NearbyRegion] = Field(default_factory=list)
    nearby_neighborhoods: list[NearbyRegion] = Field(default_factory=list)
    nearby_zipcodes: list[NearbyRegion] = Field(default_factory=list)
    # nearby_homes / comps are lazy-loaded client-side (usually empty in SSR).
    nearby_homes: list[Listing] = Field(default_factory=list)
    # Timestamps
    scraped_utc: float | None = None
    scraped_at: str | None = None


# =============================================================================
# Agent profile
# =============================================================================


class AgentReview(_BaseModel):
    """One review on a Zillow agent profile (from ``reviewsData.reviews``)."""

    rating: int | None = None
    comment: str | None = None
    date: str | None = None
    date_utc: float | None = None
    date_at: str | None = None
    work_description: str | None = None
    reviewer_name: str | None = None
    rebuttal: str | None = None
    # [{"description": "Responsiveness", "score": 5}, …]
    sub_ratings: list[dict[str, Any]] = Field(default_factory=list)


class PastSale(_BaseModel):
    """A closed transaction from an agent's ``pastSales`` block."""

    zpid: str | None = None
    street_address: str | None = None
    city_state_zip: str | None = None
    price: int | None = None
    sold_date: str | None = None
    sold_date_utc: float | None = None
    sold_date_at: str | None = None
    bedrooms: float | None = None
    bathrooms: float | None = None
    living_area: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    represented: str | None = None  # buyer / seller / both
    image_url: str | None = None
    url: str | None = None


class AgentLicense(_BaseModel):
    """A single professional license held by an agent."""

    state: str | None = None
    license_type: str | None = None
    license_number: str | None = None
    status: str | None = None
    expiration: str | None = None


class Agent(_BaseModel):
    """A Zillow real-estate professional profile (from /profile/{username})."""

    username: str | None = None
    encoded_zuid: str | None = None
    name: str | None = None
    url: str | None = None
    profile_photo: str | None = None
    phone: str | None = None
    email: str | None = None
    business_name: str | None = None
    business_address: str | None = None
    broker_name: str | None = None
    title: str | None = None
    bio: str | None = None
    rating: float | None = None
    review_count: int | None = None
    recent_sales_count: int | None = None
    total_sales_last_year: int | None = None
    for_sale_count: int | None = None
    for_rent_count: int | None = None
    past_sales_count: int | None = None
    years_experience: int | None = None
    is_top_agent: bool | None = None
    is_team_lead: bool | None = None
    license_number: str | None = None
    license_state: str | None = None
    # Social / web
    website_url: str | None = None
    facebook_url: str | None = None
    linkedin_url: str | None = None
    x_url: str | None = None
    video_url: str | None = None
    specialties: list[str] = Field(default_factory=list)
    service_areas: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    licenses: list[AgentLicense] = Field(default_factory=list)
    professional_information: list[dict[str, Any]] = Field(default_factory=list)
    reviews: list[AgentReview] = Field(default_factory=list)
    past_sales: list[PastSale] = Field(default_factory=list)
    listings: list[Listing] = Field(default_factory=list)
    scraped_utc: float | None = None
    scraped_at: str | None = None


# =============================================================================
# Autocomplete
# =============================================================================


class AutocompleteResult(_BaseModel):
    """A region/address suggestion resolved for a search term."""

    display: str | None = None
    region_id: int | None = None
    region_type: str | None = None  # city, zipcode, neighborhood, county, state
    latitude: float | None = None
    longitude: float | None = None
    zpid: str | None = None  # populated when the suggestion is a specific home
    metro_id: int | None = None


# =============================================================================
# Response envelopes
# =============================================================================


class SearchResponse(_BaseModel):
    """Response for /search."""

    location: str | None = None
    status: str = "for_sale"
    results: list[Listing] = Field(default_factory=list)
    map_results_count: int = 0
    region: RegionSelection | None = None
    map_bounds: MapBounds | None = None
    pagination: Pagination = Field(default_factory=Pagination)
    scraped_utc: float | None = None
    scraped_at: str | None = None


class PropertyResponse(_BaseModel):
    """Response for /property/{zpid}."""

    property: Property


class AgentResponse(_BaseModel):
    """Response for /agent."""

    agent: Agent


class AutocompleteResponse(_BaseModel):
    """Response for /autocomplete."""

    query: str
    results: list[AutocompleteResult] = Field(default_factory=list)


class MarketsResponse(_BaseModel):
    """Response for /markets."""

    markets: list[MarketInfo] = Field(default_factory=list)
