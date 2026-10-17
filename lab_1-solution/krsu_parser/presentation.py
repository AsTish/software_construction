from .domain import KrsuPackage


class KrsuReportFormatter:
    def format(self, package: KrsuPackage) -> str:
        lines = ["Format: KRSU"]
        for label, value in (("Checker", package.checker), ("Interactor", package.interactor),
                             ("Problem", package.problem), ("Memory limit (bytes)", package.memory_limit_bytes),
                             ("Time limit (ms)", package.time_limit_milliseconds), ("Test version", package.test_version),
                             ("Run type", package.run_type)):
            if value is not None:
                lines.append(f"{label}: {value}")
        lines.append(f"Groups: {len(package.groups)}")
        for group in package.groups:
            lines.append(f"  {group.identifier}: points={group.points}; prerequisites={','.join(group.prerequisites) or '-'}")
        lines.append(f"Tests: {len(package.tests)}")
        for index, test in enumerate(package.tests, 1):
            lines.append(f"  {index}: input={test.input_file}; output={test.output_file}; group={test.group_id or '-'}; points={test.points if test.points is not None else '-'}")
        return "\n".join(lines)
