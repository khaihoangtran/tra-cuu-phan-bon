# Frontend Reference — index.html (Card UI)

## API Contract

```
GET /columns  → { columns: [...], labels: { col: "Nhãn tiếng Việt" } }
GET /filters  → { loai_phan: [...]}
GET /search?q=&page=&loai_phan=&dam_min=&dam_max=&lan_min=&lan_max=&kali_min=&kali_max=
            → { total, pages, page, data: [{...}] }
```

## CSS Design Tokens

```css
:root {
  --bg:        #f0f4f0;   /* light green-grey page background */
  --surface:   #ffffff;   /* card background */
  --surface2:  #f7faf7;   /* input/chip background */
  --border:    #d8e6d8;   /* all borders */
  --green:     #2d7a3a;   /* primary — header, buttons, accents */
  --green-lt:  #e8f5e9;   /* card header gradient start */
  --green-mid: #4caf50;   /* search input focus ring */
  --text:      #1a2e1a;   /* body text */
  --muted:     #607060;   /* labels, secondary text */
  --tag-bg:    #e3f2e1;   /* loại phân tag background */
  --tag-text:  #2d6a34;   /* loại phân tag text */
  --r:         12px;      /* border-radius */
}
```

Fonts: `Be Vietnam Pro` (UI), `JetBrains Mono` (MSPB, dates, nutrient values).

## Card Structure (buildCard function)

```
┌─────────────────────────────────────────┐
│ HEADER (green gradient)                 │
│  [# MSPB badge]          [Status badge] │
│  Product Name (ten_san_pham)            │
│  [Loại phân tag]                        │
├─────────────────────────────────────────┤
│ BODY                                    │
│  Mã số: xxx  QĐ: xxx/QĐ-BVTV-PB       │
│                                         │
│  Thành phần dinh dưỡng                  │
│  [N 46%] [S 24%] [Zn 200ppm] ...       │
│                                         │
│  1 Lưu huỳnh (S): 24 %                 │
│  2 Độ ẩm: 1. %  ▼ Xem thêm            │
│                                         │
│  Cấp: 20/06/2024  Hết hạn: 19/06/2029  │
└─────────────────────────────────────────┘
```

## Nutrient Chips (NUTRIENTS array)

Only chips where `r[key] != null && r[key] !== ''` are rendered.

```javascript
const NUTRIENTS = [
  {key:'dam_tong_so_pct',   label:'N',      unit:'%'},
  {key:'lan_huu_hieu_pct',  label:'P₂O₅',  unit:'%'},
  {key:'kali_huu_hieu_pct', label:'K₂O',   unit:'%'},
  {key:'canxi_pct',         label:'Ca',     unit:'%'},
  {key:'magie_pct',         label:'Mg',     unit:'%'},
  {key:'luu_huynh_pct',     label:'S',      unit:'%'},
  {key:'dong_ppm',          label:'Cu',     unit:'ppm'},
  {key:'sat_ppm',           label:'Fe',     unit:'ppm'},
  {key:'kem_ppm',           label:'Zn',     unit:'ppm'},
  {key:'bo_ppm',            label:'B',      unit:'ppm'},
  {key:'mangan_ppm',        label:'Mn',     unit:'ppm'},
  {key:'chat_huu_co_pct',   label:'Hữu cơ', unit:'%'},
  {key:'axit_humic_pct',    label:'Humic',  unit:'%'},
  {key:'ph_h2o',            label:'pH',     unit:''},
];
```

To add more chips, append to this array.

## Filter Bar Wiring

```javascript
// Categorical → onchange fires immediately
<select id="filterLoai" onchange="applyFilters()">

// Numeric range → debounced 500ms (avoid firing on every keystroke)
<input type="number" id="damMin" oninput="debounceFilters()"/>

// Reset all
function resetFilters() {
  ['filterLoai'].forEach(id => document.getElementById(id).value = '');
  ['damMin','damMax','lanMin','lanMax','kaliMin','kaliMax'].forEach(id =>
    document.getElementById(id).value = '');
  currentPage = 1; fetchData();
}
```

## buildUrl() — URL construction

```javascript
function buildUrl() {
  const params = new URLSearchParams();
  params.set('q', currentQuery);
  params.set('page', currentPage);
  const loai = document.getElementById('filterLoai').value;
  if (loai)   params.set('loai_phan', loai);
  // ... same pattern for all filters
  return `${API_BASE}/search?${params.toString()}`;
}
```

## Search Highlight

```javascript
function highlight(text, q) {
  if (!q) return text;
  const re = new RegExp(`(${q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')})`, 'gi');
  return text.replace(re, '<mark>$1</mark>');
}
// mark { background: rgba(45,122,58,.15); color: var(--green); }
```

## Cards Grid

```css
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
}
```

Adjust `minmax(340px, 1fr)` to change card width. Min 300px for mobile.

## Adding a New Filter Dropdown

1. Add `<div class="filter-group">` with `<select>` in the filter bar HTML
2. Populate it from `/filters` response in `initApp()`:
   ```javascript
   populateSelect('filterMyCol', fData.my_col || []);
   ```
3. Add `params.set('my_col', ...)` in `buildUrl()`
4. Wire `onchange="applyFilters()"` on the select