from dataclasses import dataclass, field


@dataclass
class ProjectModel:
    project_name: str = ""
    context: dict[str, str] = field(default_factory=dict)
    users: list[str] = field(default_factory=list)
    role_requirements: list[str] = field(default_factory=list)
    functional_requirements: list[str] = field(default_factory=list)
    data_requirements: list[str] = field(default_factory=list)
    document_requirements: list[str] = field(default_factory=list)
    search_requirements: list[str] = field(default_factory=list)
    dashboard_requirements: list[str] = field(default_factory=list)
    map_requirements: list[str] = field(default_factory=list)
    report_requirements: list[str] = field(default_factory=list)
    export_requirements: list[str] = field(default_factory=list)
    notification_requirements: list[str] = field(default_factory=list)
    workflows: list[str] = field(default_factory=list)
    validation_rules: list[str] = field(default_factory=list)
    rejection_rules: list[str] = field(default_factory=list)
    history_requirements: list[str] = field(default_factory=list)
    security_needs: list[str] = field(default_factory=list)
    non_functional_requirements: list[str] = field(default_factory=list)
    mvp: list[str] = field(default_factory=list)
    future_features: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    points_to_validate: list[str] = field(default_factory=list)
    raw_answers: dict[str, str] = field(default_factory=dict)

