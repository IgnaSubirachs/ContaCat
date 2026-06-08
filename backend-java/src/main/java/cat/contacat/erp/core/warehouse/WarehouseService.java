package cat.contacat.erp.core.warehouse;

import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyNotFoundException;
import cat.contacat.erp.core.company.CompanyRepository;
import cat.contacat.erp.core.warehouse.api.WarehouseRequest;
import cat.contacat.erp.core.warehouse.api.WarehouseResponse;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class WarehouseService {

    private final WarehouseRepository repository;
    private final CompanyRepository companyRepository;

    public WarehouseService(WarehouseRepository repository, CompanyRepository companyRepository) {
        this.repository = repository;
        this.companyRepository = companyRepository;
    }

    @Transactional(readOnly = true)
    public List<WarehouseResponse> list(String companyId) {
        ensureCompanyExists(companyId);
        return repository.findAllByCompanyIdOrderByCodeAsc(companyId).stream()
            .map(WarehouseResponse::from)
            .toList();
    }

    @Transactional(readOnly = true)
    public WarehouseResponse get(String companyId, String warehouseId) {
        return WarehouseResponse.from(findWarehouse(companyId, warehouseId));
    }

    @Transactional
    public WarehouseResponse create(String companyId, WarehouseRequest request) {
        Company company = findCompany(companyId);
        String normalizedCode = normalizeUpper(request.code());
        ensureCodeAvailable(companyId, normalizedCode, null);

        Warehouse warehouse = new Warehouse();
        warehouse.setCompany(company);
        apply(warehouse, request, normalizedCode);
        return WarehouseResponse.from(repository.save(warehouse));
    }

    @Transactional
    public WarehouseResponse update(String companyId, String warehouseId, WarehouseRequest request) {
        Warehouse warehouse = findWarehouse(companyId, warehouseId);
        String normalizedCode = normalizeUpper(request.code());
        ensureCodeAvailable(companyId, normalizedCode, warehouseId);

        apply(warehouse, request, normalizedCode);
        return WarehouseResponse.from(repository.save(warehouse));
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
            .ifPresent(existing -> {
                throw new WarehouseAlreadyExistsException(companyId, code);
            });
    }

    private void apply(Warehouse warehouse, WarehouseRequest request, String normalizedCode) {
        warehouse.setCode(normalizedCode);
        warehouse.setName(request.name().trim());
        warehouse.setActive(request.active() == null || request.active());
    }

    private String normalizeUpper(String value) {
        return value.trim().toUpperCase(Locale.ROOT);
    }
}
