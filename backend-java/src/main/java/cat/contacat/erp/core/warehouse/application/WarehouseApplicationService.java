package cat.contacat.erp.core.warehouse.application;

import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyNotFoundException;
import cat.contacat.erp.core.company.CompanyRepository;
import cat.contacat.erp.core.warehouse.Warehouse;
import cat.contacat.erp.core.warehouse.WarehouseAlreadyExistsException;
import cat.contacat.erp.core.warehouse.WarehouseNotFoundException;
import cat.contacat.erp.core.warehouse.WarehouseRepository;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class WarehouseApplicationService {

    private final WarehouseRepository repository;
    private final CompanyRepository companyRepository;

    public WarehouseApplicationService(WarehouseRepository repository, CompanyRepository companyRepository) {
        this.repository = repository;
        this.companyRepository = companyRepository;
    }

    @Transactional(readOnly = true)
    public List<Warehouse> list(String companyId) {
        ensureCompanyExists(companyId);
        return repository.findAllByCompanyIdOrderByCodeAsc(companyId);
    }

    @Transactional(readOnly = true)
    public Warehouse get(String companyId, String warehouseId) {
        return findWarehouse(companyId, warehouseId);
    }

    @Transactional
    public Warehouse create(String companyId, WarehouseCommand command) {
        Company company = findCompany(companyId);
        String normalizedCode = normalizeUpper(command.code());
        ensureCodeAvailable(companyId, normalizedCode, null);

        Warehouse warehouse = new Warehouse();
        warehouse.setCompany(company);
        apply(warehouse, command, normalizedCode);
        return repository.save(warehouse);
    }

    @Transactional
    public Warehouse update(String companyId, String warehouseId, WarehouseCommand command) {
        Warehouse warehouse = findWarehouse(companyId, warehouseId);
        String normalizedCode = normalizeUpper(command.code());
        ensureCodeAvailable(companyId, normalizedCode, warehouseId);

        apply(warehouse, command, normalizedCode);
        return repository.save(warehouse);
    }

    @Transactional
    public void deactivate(String companyId, String warehouseId) {
        Warehouse warehouse = findWarehouse(companyId, warehouseId);
        warehouse.setActive(false);
        repository.save(warehouse);
    }

    private Warehouse findWarehouse(String companyId, String warehouseId) {
        Warehouse warehouse = repository.findById(warehouseId)
            .orElseThrow(() -> new WarehouseNotFoundException(companyId, warehouseId));

        if (!Objects.equals(warehouse.getCompany().getId(), companyId)) {
            throw new WarehouseNotFoundException(companyId, warehouseId);
        }
        return warehouse;
    }

    private Company findCompany(String companyId) {
        return companyRepository.findById(companyId)
            .orElseThrow(() -> new CompanyNotFoundException(companyId));
    }

    private void ensureCompanyExists(String companyId) {
        if (!companyRepository.existsById(companyId)) {
            throw new CompanyNotFoundException(companyId);
        }
    }

    private void ensureCodeAvailable(String companyId, String code, String currentWarehouseId) {
        repository.findByCompanyIdAndCode(companyId, code)
            .filter(existing -> !Objects.equals(existing.getId(), currentWarehouseId))
            .ifPresent(existing -> { throw new WarehouseAlreadyExistsException(companyId, code); });
    }

    private void apply(Warehouse warehouse, WarehouseCommand command, String normalizedCode) {
        warehouse.setCode(normalizedCode);
        warehouse.setName(command.name().trim());
        warehouse.setActive(command.active() == null || command.active());
    }

    private String normalizeUpper(String value) {
        return value.trim().toUpperCase(Locale.ROOT);
    }
}
