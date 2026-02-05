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

    loadChildren({
        url: `/ads/ajax/category_children/${categoryId}/`,
        callback: data => {
            if (data.items.length) {
                let selectElement = addDropdown({
                    sectionId: sectionId,
                    level: level + 1,
                    labelText: 'Category: ' + level,
                    options: data.items,
                    valueKey: 'categoryId',
                    onChange: handleCategoryChange
                });
                if (pageContext && pageContext.category_hierarchy) {
                    selectOptionFromArray({
                        selectElement: selectElement,
                        targetArray: pageContext.category_hierarchy.map(category => category.id)
                    });
                }
            } else {
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
        }
    });
}

function initLocationFlow() {
    loadChildren({
        url: '/ads/ajax/locations/',
        callback: data => {
            let selectElement = addDropdown({
                sectionId: 'location_section',
                level: 1,
                labelText: 'Location',
                options: data.items,
                valueKey: 'locationId',
                onChange: handleLocationChange
            });
            if (pageContext.location_hierarchy && pageContext.location_hierarchy.location) {
                selectOptionFromArray({
                    selectElement: selectElement,
                    targetArray: [pageContext.location_hierarchy.location.id]
                });
            }
        }
    });
}

function handleLocationChange({ sectionId, locationId, level }) {
    clearNeighbourhood({ sectionId: sectionId, level: level });
    if (!locationId) return;

    loadChildren({
        url: `/ads/ajax/cities/${locationId}/`,
        callback: data => {
            let selectElement = addDropdown({
                sectionId: sectionId,
                level: level + 1,
                labelText: 'City',
                options: data.items,
                valueKey: 'cityId',
                onChange: handleCityChange
            });
            if (pageContext.location_hierarchy && pageContext.location_hierarchy.city) {
                selectOptionFromArray({
                    selectElement: selectElement,
                    targetArray: [pageContext.location_hierarchy.city.id]
                });
            }
        }
    });
}

function handleCityChange({ sectionId, cityId, level }) {
    clearNeighbourhood({ sectionId: sectionId, level: level });
    if (!cityId) return;

    loadChildren({
        url: `/ads/ajax/neighbourhoods/${cityId}/`,
        callback: data => {
            if (data.items.length) {
                let selectElement = addDropdown({
                    sectionId: sectionId,
                    level: level + 1,
                    labelText: 'Neighbourhood',
                    options: data.items,
                    valueKey: 'neighbourhoodId',
                    onChange: handleNeighbourhoodChange
                });
                if (pageContext.location_hierarchy && pageContext.location_hierarchy.neighbourhood) {
                    selectOptionFromArray({
                        selectElement: selectElement,
                        targetArray: [pageContext.location_hierarchy.neighbourhood.id]
                    });
                }
            }
        }
    });
}

function handleNeighbourhoodChange({ sectionId, neighbourhoodId }) {
    document.getElementById('id_neighbourhood').value = neighbourhoodId;
}

function clearNeighbourhood({ sectionId, level }) {
    removeChildDropdowns({ sectionId: sectionId, fromLevel: level + 1 });
    document.getElementById('id_neighbourhood').value = '';
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
