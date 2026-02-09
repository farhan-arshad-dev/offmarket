document.addEventListener('DOMContentLoaded', function () {
    // pre-loaded data (category and location hierarchy)
    window.pageContext = JSON.parse(document.getElementById('page-context').textContent);
    initiateCategoryFlow();
    initLocationFlow();
})

function initiateCategoryFlow() {
    // load main category
    handleCategoryChange({ sectionId: 'category_section', categoryId: 0, level: 0 });
}

function handleCategoryChange({ sectionId, categoryId = null, level }) {
    removeChildDropdowns({ sectionId: sectionId, fromLevel: level + 1 });
    document.getElementById('id_category').value = '';
    document.getElementById('property-container').innerHTML = '';

    const id = Number(categoryId);
    if (!Number.isInteger(id)) return;
    loadAndRenderDropdown({
        url: `/ads/ajax/category_children/${categoryId}/`,
        sectionId: sectionId,
        level: level + 1,
        labelText: 'Category: ' + level,
        valueKey: 'categoryId',
        onChange: handleCategoryChange,
        preselectIds: pageContext?.category_hierarchy?.map(category => category.id) || null,
        onEmpty: () => {
            document.getElementById('id_category').value = categoryId;
            let adElement = document.getElementById('id_ad');

            if (categoryId && adElement) {
                let adId = adElement.dataset.adId;
                loadChildren({
                    url: `/ads/ajax/load-category-properties/?category_id=${categoryId}&ad_id=${adId}`,
                    callback: data => {
                        document.getElementById('property-container').innerHTML = data.html;
                    }
                });
            }
        }
    });
}

function initLocationFlow() {
    loadAndRenderDropdown({
        url: '/ads/ajax/locations/',
        sectionId: 'location_section',
        level: 1,
        labelText: 'Location',
        valueKey: 'locationId',
        onChange: handleLocationChange,
        preselectIds: pageContext?.location_hierarchy?.location ? [pageContext.location_hierarchy.location.id] : null
    });
}

function handleLocationChange({ sectionId, locationId, level }) {
    clearNeighbourhood({ sectionId: sectionId, level: level });
    if (!locationId) return;

    loadAndRenderDropdown({
        url: `/ads/ajax/cities/${locationId}/`,
        sectionId,
        level: level + 1,
        labelText: 'City',
        valueKey: 'cityId',
        onChange: handleCityChange,
        preselectIds: pageContext?.location_hierarchy?.city ? [pageContext.location_hierarchy.city.id] : null
    });
}

function handleCityChange({ sectionId, cityId, level }) {
    clearNeighbourhood({ sectionId: sectionId, level: level });
    if (!cityId) return;
    loadAndRenderDropdown({
        url: `/ads/ajax/neighbourhoods/${cityId}/`,
        sectionId,
        level: level + 1,
        labelText: 'Neighbourhood',
        valueKey: 'neighbourhoodId',
        onChange: handleNeighbourhoodChange,
        preselectIds: pageContext?.location_hierarchy?.neighbourhood ? [pageContext.location_hierarchy.neighbourhood.id] : null
    });
}

function handleNeighbourhoodChange({ sectionId, neighbourhoodId }) {
    document.getElementById('id_neighbourhood').value = neighbourhoodId;
}

function clearNeighbourhood({ sectionId, level }) {
    removeChildDropdowns({ sectionId: sectionId, fromLevel: level + 1 });
    document.getElementById('id_neighbourhood').value = '';
}

function loadAndRenderDropdown({ url, sectionId, level, labelText, valueKey, onChange, preselectIds = null, onEmpty = null }) {
    loadChildren({
        url,
        callback: data => {
            if (!data.items || !data.items.length) {
                if (typeof onEmpty === 'function') {
                    onEmpty();
                }
                return;
            }
            let selectElement = addDropdown({
                sectionId: sectionId, level: level, labelText: labelText,
                options: data.items, valueKey: valueKey, onChange: onChange
            });
            if (preselectIds) {
                selectOptionFromArray({ selectElement: selectElement, targetArray: preselectIds });
            }
        }
    });
}

function loadChildren({ url, callback }) {
    fetch(url).then(response => response.json()).then(callback).catch(error => {
        console.error('Failed to load data', error);
    });
}

function addDropdown({ sectionId, level, labelText, options, valueKey, onChange }) {
    const section = document.getElementById(sectionId);
    removeChildDropdowns({ sectionId, fromLevel: level });

    const paragraph = document.createElement('p');
    paragraph.dataset.level = level;

    const label = document.createElement('label');
    label.textContent = labelText;
    paragraph.appendChild(label);

    const selectElement = document.createElement('select');
    selectElement.classList.add('form-control');

    selectElement.appendChild(
        prepareOption({ value: '', text: '---------' })
    );

    options.forEach(item => {
        selectElement.appendChild(prepareOption({ value: item.id, text: item.name }));
    });

    selectElement.onchange = e => onChange({
        sectionId: sectionId, [valueKey]: e.target.value, level: level
    });

    paragraph.appendChild(selectElement);
    section.appendChild(paragraph);

    return selectElement;
}

function prepareOption({ value, text }) {
    let option = document.createElement('option');
    option.value = value;
    option.text = text;
    return option;
}

function removeChildDropdowns({ sectionId, fromLevel }) {
    const section = document.getElementById(sectionId);
    const paragraphs = section.querySelectorAll('p');

    paragraphs.forEach(p => {
        const level = parseInt(p.dataset.level, 10);

        if (!isNaN(level) && level >= fromLevel) {
            p.remove();
        }
    })
}

function selectOptionFromArray({ selectElement, targetArray }) {
    let valueToSelect = '';
    for (const value of targetArray) {
        const optionExists = selectElement.querySelector(`option[value='${value}']`) !== null;
        if (optionExists) {
            valueToSelect = value;
            break;
        }
    }
    selectElement.value = valueToSelect;
    selectElement.dispatchEvent(new Event('change'));
}
