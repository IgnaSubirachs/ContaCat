package cat.contacat.erp.architecture;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.classes;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noFields;
import static com.tngtech.archunit.library.dependencies.SlicesRuleDefinition.slices;

import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.junit.AnalyzeClasses;
import com.tngtech.archunit.junit.ArchTest;
import com.tngtech.archunit.lang.ArchRule;
import org.springframework.beans.factory.annotation.Autowired;

@AnalyzeClasses(packages = "cat.contacat.erp", importOptions = ImportOption.DoNotIncludeTests.class)
class ArchitectureRulesTest {

    @ArchTest
    static final ArchRule controllers_must_live_in_api_packages =
        classes()
            .that().haveSimpleNameEndingWith("Controller")
            .should().resideInAPackage("..api..");

    @ArchTest
    static final ArchRule controllers_must_not_depend_on_repositories =
        noClasses()
            .that().haveSimpleNameEndingWith("Controller")
            .should().dependOnClassesThat().haveSimpleNameEndingWith("Repository");

    @ArchTest
    static final ArchRule repositories_must_be_interfaces =
        classes()
            .that().haveSimpleNameEndingWith("Repository")
            .should().beInterfaces();

    @ArchTest
    static final ArchRule services_must_not_live_in_api_packages =
        noClasses()
            .that().haveSimpleNameEndingWith("Service")
            .should().resideInAPackage("..api..");

    @ArchTest
    static final ArchRule application_layer_must_not_depend_on_api_dtos =
        noClasses()
            .that().resideInAPackage("..application..")
            .should().dependOnClassesThat().resideInAPackage("..api..");

    @ArchTest
    static final ArchRule field_injection_is_forbidden =
        noFields()
            .should().beAnnotatedWith(Autowired.class);

    @ArchTest
    static final ArchRule core_modules_must_be_cycle_free =
        slices()
            .matching("cat.contacat.erp.core.(*)..")
            .should().beFreeOfCycles();
}
